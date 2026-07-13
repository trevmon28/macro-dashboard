# Feature Specification: Macro Dashboard MCP Server — VPS Deployment

**Feature:** `002-mcp-server-vps`
**Author:** Trevor Monroe
**Date:** July 2026
**Status:** Deployed (July 11, 2026)

---

## Overview

Expose the Global Macro Dashboard data as an MCP server running on the existing VPS, reachable at `https://macro-mcp.trevormonroe.com/mcp`. This allows Claude AI and other MCP-compatible clients to query live macro indicators, yield curve data, recession probability, and country scoreboard data interactively.

**NOTE: The original spec assumed Nginx + certbot, but this server uses Traefik (Docker) as the reverse proxy. Do NOT attempt to use Nginx — it cannot start because Traefik owns ports 80 and 443. See the Traefik section below.**

---

## VPS Host Configuration

| Field | Value |
|-------|-------|
| IP address | `129.121.100.134` |
| OS | AlmaLinux (cPanel VPS — NOT Ubuntu) |
| SSH | `ssh -i C:\Users\trevm\.ssh\id_mlb_vps root@129.121.100.134` |
| Deploy path | `/opt/macro/` |
| Service user | `root` (`www-data` does not exist on this server) |
| Python | `python3.11` (system `python3` is 3.9 — too old for imf-reader/wbdata) |
| Virtualenv | `/opt/macro/venv/` |
| Internal port | `9002` |
| External URL | `https://macro-mcp.trevormonroe.com/mcp` |
| Health endpoint | `https://macro-mcp.trevormonroe.com/health` |
| Systemd service | `/etc/systemd/system/macro-mcp.service` |
| Traefik route config | `/opt/hostedapps/dynamic/macro-mcp.toml` |
| Data dir | `/opt/macro/data/outputs/` |

**DNS record:**
```
macro-mcp.trevormonroe.com.  A  129.121.100.134
```
Add via cPanel → Zone Editor → Manage trevormonroe.com → Add A Record.

---

## MCP Tools to Expose

| Tool | Description | Data source |
|------|-------------|-------------|
| `get_macro_snapshot` | Latest values for all US indicators (yield spread, recession prob, inflation regime, risk score) | `data/outputs/latest_snapshot.json` |
| `get_yield_curve` | Yield curve spread history (10y–2y and 10y–3m) with inversion signal | `data/outputs/indicators.parquet` |
| `get_recession_probability` | Recession probability time series with current reading | `data/outputs/indicators.parquet` |
| `get_country_scoreboard` | Country-level GDP, inflation, unemployment, policy rates, stock YTD for 12 major economies | `data/outputs/country_scoreboard.parquet` |
| `check_pipeline_health` | Pipeline freshness — reports when outputs were last generated and whether they are stale (>7 days) | `data/outputs/latest_snapshot.json` mtime |

---

## Functional Requirements

### FR-001: Five MCP tools exposed and functional
The server must expose the five tools listed above over MCP streamable-HTTP transport.

### FR-002: Streamable-HTTP transport with valid TLS
Reachable at `https://macro-mcp.trevormonroe.com/mcp` with a valid Let's Encrypt certificate.

### FR-003: SSE streaming must reach the client
Nginx must not buffer SSE chunks. Required proxy headers (same as MLB server):
```nginx
proxy_buffering    off;
proxy_cache        off;
proxy_read_timeout 300s;
chunked_transfer_encoding on;
add_header         X-Accel-Buffering no;
```

### FR-004: Service restarts automatically on failure
Systemd service must have `Restart=always` with `RestartSec=5`.

### FR-005: Health endpoint returns 200
`GET /health` returns `{"status": "ok", "service": "macro-dashboard"}` with HTTP 200.

### FR-006: Stale data detection
`check_pipeline_health` reports stale when `latest_snapshot.json` is older than 7 days (weekly pipeline cadence). Should report the `as_of` date from the snapshot and the file mtime.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| MCP framework | `mcp` Python package (FastMCP), streamable-HTTP transport |
| ASGI server | `uvicorn` |
| Reverse proxy | **Traefik** (Docker container, NOT Nginx) |
| TLS | Let's Encrypt via Traefik `challenger` cert resolver |
| Process manager | systemd (`macro-mcp.service`) |
| Data store | Local filesystem — parquet + JSON written by weekly GitHub Actions pipeline |
| Language | Python 3.11 |

---

## Reverse Proxy: Traefik

This server uses Traefik running in Docker as the reverse proxy. **Do not attempt to install or start Nginx** — it will fail because Traefik owns ports 80 and 443.

- Traefik static config: `/opt/hostedapps/traefik.toml`
- Dynamic config directory: `/opt/hostedapps/dynamic/` (maps to `/etc/traefik/dynamic` inside container)
- `watch = true` is set — Traefik hot-reloads new `.toml` files automatically, no restart needed
- SSL cert resolver name: `challenger` (Let's Encrypt HTTP-01)
- Docker host gateway IP (for routing from container to host): `172.18.0.1`

Other services in `/opt/hostedapps/dynamic/`: `mlb.toml`, `baseball.toml`, `college-ranker.toml`, `flood.toml`

**`/opt/hostedapps/dynamic/macro-mcp.toml`:**
```toml
[http.routers]
  [http.routers.macro-mcp]
    rule = "Host(`macro-mcp.trevormonroe.com`)"
    service = "macro-mcp"
    entryPoints = ["websecure"]
    [http.routers.macro-mcp.tls]
      certResolver = "challenger"

[http.services]
  [http.services.macro-mcp.loadBalancer]
    [[http.services.macro-mcp.loadBalancer.servers]]
      url = "http://172.18.0.1:9002"
```

---

## Data Flow

The MCP server is read-only. Data is written by the GitHub Actions weekly pipeline (every Monday) and synced to the VPS:

```
GitHub Actions (weekly) → commits data/outputs/ to repo
VPS cron (weekly, after Actions) → git pull /opt/macro → MCP tools see fresh data
```

Alternatively, `data/outputs/` can be synced directly via `rsync` or `scp` after each Actions run.

---

## Deployment Procedure (Verified July 11, 2026)

### Step 1 — SSH in
```bash
ssh -i C:\Users\trevm\.ssh\id_mlb_vps root@129.121.100.134
```

### Step 2 — Clone repo
```bash
mkdir -p /opt/macro && cd /opt/macro
git clone https://github.com/trevmon28/macro-dashboard.git .
```

### Step 3 — Create venv with Python 3.11
```bash
# System python3 is 3.9 — too old. Must use python3.11.
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
pip install "mcp[cli]" uvicorn   # mcp and uvicorn not yet in requirements.txt
```

### Step 4 — Create data directory
```bash
mkdir -p data/outputs
# Note: chown www-data fails — www-data does not exist. Run as root, skip chown.
```

### Step 5 — Create systemd service
```bash
cat > /etc/systemd/system/macro-mcp.service << 'EOF'
[Unit]
Description=Global Macro Dashboard MCP Server
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/macro
Environment=MCP_TRANSPORT=http
Environment=MCP_PORT=9002
ExecStart=/opt/macro/venv/bin/python mcp_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload && systemctl enable macro-mcp && systemctl start macro-mcp
curl http://localhost:9002/health   # Expected: {"status":"ok","service":"macro-dashboard"}
```

### Step 6 — Create Traefik dynamic config
```bash
cat > /opt/hostedapps/dynamic/macro-mcp.toml << 'EOF'
[http.routers]
  [http.routers.macro-mcp]
    rule = "Host(`macro-mcp.trevormonroe.com`)"
    service = "macro-mcp"
    entryPoints = ["websecure"]
    [http.routers.macro-mcp.tls]
      certResolver = "challenger"

[http.services]
  [http.services.macro-mcp.loadBalancer]
    [[http.services.macro-mcp.loadBalancer.servers]]
      url = "http://172.18.0.1:9002"
EOF
# Traefik auto-reloads — no restart needed
```

### Step 7 — Add DNS A record
In cPanel → Zone Editor → Manage trevormonroe.com → Add Record:
- Name: `macro-mcp.trevormonroe.com`
- Type: `A`
- Record: `129.121.100.134`

### Step 8 — Verify end-to-end (after DNS propagation)
```bash
curl https://macro-mcp.trevormonroe.com/health
# Expected: {"status":"ok","service":"macro-dashboard"}
```

### Step 9 — Weekly data sync cron
```bash
# Pull fresh data/outputs/ from repo every Monday at 07:00 UTC
(crontab -l 2>/dev/null; echo "0 7 * * 1 cd /opt/macro && git pull >> /opt/macro/data/sync.log 2>&1") | crontab -
```

---

## Systemd Service

```ini
[Unit]
Description=Global Macro Dashboard MCP Server
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/macro
Environment=MCP_TRANSPORT=http
Environment=MCP_PORT=9002
ExecStart=/opt/macro/venv/bin/python mcp_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Critical:** `User=root` (not `www-data`). `MCP_PORT=9002` must not conflict with MLB server on `9003`.

---

## Known Issues (Discovered During Deploy — July 11, 2026)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `chown www-data` fails | `www-data` user doesn't exist on AlmaLinux/cPanel | Use `User=root` in systemd service, skip chown |
| `imf-reader`/`wbdata` not found by pip | System `python3` is 3.9, packages require ≥3.10 | Use `python3.11 -m venv venv` |
| `mcp` and `uvicorn` not installed | Not in `requirements.txt` | `pip install "mcp[cli]" uvicorn` after main install |
| Nginx fails to start | Traefik owns ports 80/443 | Don't use Nginx — create `/opt/hostedapps/dynamic/macro-mcp.toml` |
| `/health` returns 404 | Old squatter process on port 9002 | `fuser -k 9002/tcp && systemctl restart macro-mcp` |
| Port already in use on service restart | Previous process didn't release port | `fuser -k 9002/tcp` to clear, then restart |
| `deploy/macro-mcp.service` not found | `deploy/` dir not committed to git | Create service file directly with `cat > /etc/systemd/...` |

---

## Client Configuration

**Claude.ai (remote MCP — recommended):**
```json
{
  "mcpServers": {
    "macro-dashboard": {
      "url": "https://macro-mcp.trevormonroe.com/mcp"
    }
  }
}
```

**Claude Desktop (local stdio — development only):**
```json
{
  "mcpServers": {
    "macro-dashboard": {
      "command": "python",
      "args": ["C:/Users/trevm/Projects/macro-dashboard/mcp_server.py"]
    }
  }
}
```

**Manual server test (VPS terminal):**
```bash
MCP_TRANSPORT=http MCP_PORT=9002 /opt/macro/venv/bin/python mcp_server.py
curl http://localhost:9002/health
systemctl status macro-mcp
journalctl -u macro-mcp -n 50 --no-pager
git pull && systemctl restart macro-mcp
```

---

## Relationship to MLB MCP Server

Both servers share the same VPS (`129.121.100.134`) and Traefik reverse proxy. Key differences:

| | MLB Server | Macro Server |
|---|---|---|
| Subdomain | `mlb-mcp.trevormonroe.com` | `macro-mcp.trevormonroe.com` |
| Internal port | `9003` | `9002` |
| Deploy path | `/opt/mlb/` | `/opt/macro/` |
| Traefik config | `/opt/hostedapps/dynamic/mlb.toml` | `/opt/hostedapps/dynamic/macro-mcp.toml` |
| Systemd service | `mlb-mcp.service` | `macro-mcp.service` |
| Data pipeline | VPS cron (daily) | GitHub Actions (weekly) + VPS git pull |
