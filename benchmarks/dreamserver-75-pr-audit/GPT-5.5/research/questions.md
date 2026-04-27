# Questions Log

## Is documentation-only automatically mergeable?

Resolved: no. #1055 and #973 show docs can encode broken or stale operational/security behavior. Docs-only lowers code risk, but not project risk.

## Should direct API paths matter if the dashboard UI blocks the action?

Resolved: yes. DreamServer's dashboard-api is a server boundary. Direct `POST`/API callers can bypass UI affordances, so enforcement belongs server-side too.

## Is a compose fragment valid if `docker compose config` passes standalone?

Resolved: not necessarily. Extension fragments interact through merged stack dependencies and env interpolation. Compose proof should include required base/dependency fragments.

## How should AMD multi-GPU be judged without local AMD hardware?

Resolved: mark simulated proof explicitly and require hardware validation before merge. Passing synthetic tests is useful but insufficient for a flagship AMD partnership feature.

## How to handle bounty tier when metadata lacks labels?

Resolved: record "not found in fetched metadata" and require maintainer payout cross-check. Do not infer exact bounty tier from effort alone.
