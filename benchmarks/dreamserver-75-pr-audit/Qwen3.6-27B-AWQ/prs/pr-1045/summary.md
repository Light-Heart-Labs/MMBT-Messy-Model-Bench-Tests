# PR #1045 Summary

**Title:** fix(dashboard-api,host-agent): route extension config sync through host agent
**Author:** yasinBursali
**Created:** 2026-04-25
**Files changed:** 4
**Lines changed:** 624 (+569/-55)
**Subsystems:** host-agent, extensions
**Labels:** None

## What the PR does

## Summary

`_sync_extension_config` in `routers/extensions.py` calls `shutil.copytree` to copy `<ext_dir>/config/*` into `INSTALL_DIR/config/`. The dashboard-api container has `/dream-server/config` bind-mounted **read-only** (`docker-compose.base.yml:176`, present since v2.0.0), so the copy fails:

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py

