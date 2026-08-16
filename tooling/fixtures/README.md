# Frozen fixtures (offline task families)

Per the preregistration protocol (section 3), `p3_market` runs against a
frozen offline snapshot corpus instead of the live web. The v1 task brief
(`tooling/tasks/task_market_research.md`) is unchanged; the offline variant is
`tooling/tasks/v2/task_market_research.md`.

## Layout

- `p3_market/index.json` — corpus manifest: per snapshot `url`, `final_url`,
  `path`, `http_status`, `content_type`, `fetch_time_utc`, `sha256`, `bytes`;
  plus an `unfetchable` list for targets that could not be snapshotted.
- `p3_market/pages/` — the frozen response bodies (curl-fetched, decoded).
- `serve_fixtures.py` — deterministic stdlib HTTP mirror. A snapshot of
  `https://<host>/<path>` is served at `/<host>/<path>`; `/` is the catalog,
  `/index.json` the raw manifest. All response headers are fixed (frozen Date)
  so every response is byte-identical across requests.
- `check_fixture_determinism.py` — protocol gate: fetches every fixture URL
  twice through the running server; requires byte-identical responses that
  match the index sha256. Non-zero exit = fixture fails the determinism check
  and `p3_market` is demoted to exploratory (recorded in DEVIATIONS.md).

## Campaign wiring

1. One-time per host (subnet chosen clear of the existing 172.17–172.21
   docker subnets):

   ```
   docker network create --internal --subnet 172.29.0.0/24 \
       --gateway 172.29.0.1 mmbt-p3-offline
   ```

2. Runner starts the mirror as a container pinned at 172.29.0.2 before
   p3_market cells (Docker >= 28 blocks container-to-host traffic on
   `--internal` networks, so a host-bound server is NOT reachable from the
   sandbox — the server must live on the network itself; verified on tower2,
   Docker 29.2.1):

   ```
   docker run -d --rm --name mmbt-fixture-server \
       --network mmbt-p3-offline --ip 172.29.0.2 \
       -v <repo>/tooling/fixtures:/fixtures:ro \
       bench-sandbox:latest \
       python3 /fixtures/serve_fixtures.py --root /fixtures/p3_market \
       --host 0.0.0.0 --port 8377
   ```

3. p3_market cells pass `--sandbox-network mmbt-p3-offline` to
   `tooling/harness.py` (recorded in `receipt.json` under
   `sandbox_runtime.sandbox_network`). On the `--internal` network the
   sandbox has no route to the internet; the mirror is reachable at
   `http://172.29.0.2:8377`, the address hard-coded in the v2 brief. All
   other task families keep the default `bridge` network.

4. Gate before campaign start (host-to-container works on an internal
   network; only container-to-host is blocked):

   ```
   python3 tooling/fixtures/check_fixture_determinism.py \
       --base-url http://172.29.0.2:8377
   ```

## Known corpus limitations

- Snapshots are single curl fetches (Chrome UA, `--compressed`, redirects
  followed); JS-only content is not rendered. In particular the LastPass
  pricing snapshot does not expose explicit per-seat prices in static HTML;
  agents must flag such facts as not verifiable offline (the v2 brief says
  exactly this).
- `unfetchable` targets (403/404/429/DNS) are listed in `index.json`;
  substitutes were snapshotted where the content moved.
- Sub-resources (CSS/JS/images) are not mirrored; only the documents above.
