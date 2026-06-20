# Feature Specification: Macro Dashboard MCP Server — VPS Deployment

**Feature:** `002-mcp-server-vps`
**Author:** Trevor Monroe
**Date:** June 2026
**Status:** Planned

---

## Overview

Expose the Global Macro Dashboard data as an MCP server running on the existing VPS, reachable at `https://macro-mcp.trevormonroe.com/mcp`. This allows Claude AI and other MCP-compatible clients to query live macro indicators, yield curve data, recession probability, and country scoreboard data interactively.

The deployment pattern mirrors the MLB Prediction MCP server (`mlb-mcp.trevormonroe.com`) — same VPS, same systemd + Nginx + certbot stack, different port and subdomain. See `C:\Users\trevm\Projects\MLBPrediction\specs\002-mcp-server-vps\` for the reference implementation.

---

## VPS Host Configuration

| Field | Value |
|-------|-------|
| IP address | `129.121.100.134` |
| OS | Ubuntu 22.04 LTS (cPanel VPS) |
| Deploy path | `/opt/macro/` |
| Service user | `www-data` |
| Internal port | `9002` (avoids conflict with MLB server on `9001`) |
| External port | `443` (Nginx TLS termination) |
| Domain | `macro-mcp.trevormonroe.com` |
| MCP endpoint | `https://macro-mcp.trevormonroe.com/mcp` |
| Health endpoint | `https://macro-mcp.trevormonroe.com/health` |
| Nginx config | `/etc/nginx/sites-available/macro-mcp` |
| Systemd service | `/etc/systemd/system/macro-mcp.service` |
| Virtualenv | `/opt/macro/venv/` |
| Data dir | `/opt/macro/data/outputs/` (snapshot JSON, indicator parquets) |

**DNS record required:**
```
macro-mcp.trevormonroe.com.  A  129.121.100.134
```

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
| ASGI server | `uvicorn` (embedded in FastMCP) |
| Reverse proxy | Nginx (TLS termination, SSE headers, subdomain routing) |
| TLS | Let's Encrypt via certbot (auto-renewal) |
| Process manager | systemd (`macro-mcp.service`) |
| Data store | Local filesystem — parquet + JSON written by weekly GitHub Actions pipeline |
| Language | Python 3.11+ |

---

## Data Flow

The MCP server is read-only. Data is written by the GitHub Actions weekly pipeline (every Monday) and synced to the VPS:

```
GitHub Actions (weekly) → commits data/outputs/ to repo
VPS cron (weekly, after Actions) → git pull /opt/macro → MCP tools see fresh data
```

Alternatively, `data/outputs/` can be synced directly via `rsync` or `scp` after each Actions run.

---

## Deployment Procedure

### Step 1 — System packages (if not already installed for MLB server)
```bash
apt update && apt install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

### Step 2 — Clone repo and install dependencies
```bash
cd /opt
git clone https://github.com/trevmon28/macro-dashboard.git macro
cd macro
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
```

### Step 3 — Create data directories and fix permissions
```bash
mkdir -p data/outputs data/raw data/processed
chown -R www-data:www-data /opt/macro
```

### Step 4 — Add FRED API key to environment
```bash
echo "FRED_API_KEY=your_key_here" > /opt/macro/.env
chown www-data:www-data /opt/macro/.env
chmod 600 /opt/macro/.env
```

### Step 5 — Run initial pipeline to populate data/outputs/
```bash
sudo -u www-data bash -c "
  source /opt/macro/venv/bin/activate
  cd /opt/macro
  TODAY=$(date -u +%Y-%m-%d)
  papermill notebooks/01_ingest.ipynb /tmp/01_out.ipynb -p run_date \$TODAY
  papermill notebooks/02_transform.ipynb /tmp/02_out.ipynb -p run_date \$TODAY
  papermill notebooks/03_model.ipynb /tmp/03_out.ipynb -p run_date \$TODAY
"
```

### Step 6 — Install and start systemd service
```bash
cp deploy/macro-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable macro-mcp
systemctl start macro-mcp
# Verify:
systemctl status macro-mcp --no-pager
curl http://localhost:9002/health   # should return {"status":"ok"}
```

### Step 7 — Install Nginx config
```bash
cp deploy/nginx-macro-mcp.conf /etc/nginx/sites-available/macro-mcp
ln -sf /etc/nginx/sites-available/macro-mcp /etc/nginx/sites-enabled/macro-mcp
nginx -t && systemctl reload nginx
```

### Step 8 — Add DNS A record
```
macro-mcp.trevormonroe.com  A  129.121.100.134
```
Wait for propagation: `dig macro-mcp.trevormonroe.com` must return `129.121.100.134`.

### Step 9 — Issue SSL certificate
```bash
certbot --nginx -d macro-mcp.trevormonroe.com
```

### Step 10 — Verify end-to-end
```bash
curl https://macro-mcp.trevormonroe.com/health
# Expected: {"status":"ok","service":"macro-dashboard"}
```

### Step 11 — Install weekly sync cron
```bash
# Pull fresh data/outputs/ from repo every Monday at 07:00 UTC (after Actions run at 06:00)
(crontab -u www-data -l 2>/dev/null; echo "0 7 * * 1 cd /opt/macro && git pull >> data/sync.log 2>&1") | crontab -u www-data -
```

---

## Nginx Config

```nginx
server {
    listen 80;
    server_name macro-mcp.trevormonroe.com;

    location / {
        proxy_pass         http://127.0.0.1:9002;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        # Required for MCP streamable-HTTP / SSE
        proxy_buffering    off;
        proxy_cache        off;
        proxy_read_timeout 300s;
        chunked_transfer_encoding on;
        add_header         X-Accel-Buffering no;
    }
}
# certbot appends HTTPS block automatically
```

---

## Systemd Service

```ini
[Unit]
Description=Global Macro Dashboard MCP Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/macro
EnvironmentFile=/opt/macro/.env
Environment=MCP_TRANSPORT=http
Environment=MCP_PORT=9002
ExecStart=/opt/macro/venv/bin/python mcp_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Critical:** `MCP_PORT=9002` must match the Nginx `proxy_pass` target. Do not use port 9001 (reserved for MLB MCP server on this VPS).

---

## Known Issues / Setup Friction

These mirror the MLB server issues — read before attempting deploy:

### Port conflict with MLB server
MLB server runs on `9001`. This server uses `9002`. Running manually without setting `MCP_PORT=9002` will fall back to the code default and may conflict. Always run manually as:
```bash
MCP_TRANSPORT=http MCP_PORT=9002 python mcp_server.py
```

### DNS must propagate before certbot
Same as MLB server — wait for `dig macro-mcp.trevormonroe.com` to return the correct IP before running certbot.

### Data freshness — pipeline runs on GitHub Actions, not VPS
Unlike the MLB server (which runs its pipeline on the VPS via cron), the macro pipeline runs in GitHub Actions and commits outputs to the repo. The VPS `git pull` cron (Step 11) pulls fresh outputs weekly. If Actions is disabled or the pipeline fails, `data/outputs/` on the VPS will go stale. `check_pipeline_health` detects this.

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

Both servers share the same VPS (`129.121.100.134`) and the same deployment pattern. Key differences:

| | MLB Server | Macro Server |
|---|---|---|
| Subdomain | `mlb-mcp.trevormonroe.com` | `macro-mcp.trevormonroe.com` |
| Port | `9001` | `9002` |
| Deploy path | `/opt/mlb/` | `/opt/macro/` |
| Data pipeline | VPS cron (daily) | GitHub Actions (weekly) + VPS git pull |
| Systemd service | `mlb-mcp.service` | `macro-mcp.service` |
| Nginx config | `mlb-mcp` in sites-available | `macro-mcp` in sites-available |
