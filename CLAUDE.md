# CLAUDE.md

## Shared VPS

`macro-mcp` (`/opt/macro` on the VPS) runs on a shared Bluehost VPS used by
several other projects. See `C:\Users\trevm\Projects\VPS.md` for host access,
all services on the box, and known gotchas.

**Important:** unlike the other services on this box, `macro-mcp` is **not**
included in `/opt/update-mcps.sh`'s scope at all — there is no automated
deploy for it. Code changes here require a manual deploy on the VPS
(`ssh root@129.121.100.134`, `cd /opt/macro && git pull && systemctl restart
macro-mcp`).
