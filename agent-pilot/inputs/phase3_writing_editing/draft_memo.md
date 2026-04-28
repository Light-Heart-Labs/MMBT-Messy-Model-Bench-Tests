# Internal: What Happened on Friday + Where We Land On It

So, ok, this is going to be long. Sorry. I want to write up the whole sequence of what happened with the 4-hour outage we had Friday before the noise from the customer side gets too far ahead of where we actually are. I'm going to try to be honest about what we got wrong because I think that matters more than the spin we'd want to put on it. So bear with me.

The short version: from approximately 14:11 UTC to 18:24 UTC on Friday, our primary API was returning 502s for somewhere between 60% and 100% of inbound requests across all customer accounts. Status page was green for the first ~40 minutes because our status-page check was using the wrong endpoint, which, ok, that's its own issue. We've fixed that already, but let's come back to it.

What broke: someone on the platform team (it was Marcus, and he's been told this is not a blame thing — the system shouldn't have allowed this in the first place) deployed a config change at 14:09 UTC that updated the rate-limit thresholds for our internal authentication service. The change doubled the threshold values, which seemed safe — bigger numbers should mean fewer rate-limit rejections. But the auth service has a separate internal limiter that uses a fraction of the global threshold, and that fraction is computed against a hard-coded MAX value, not the new configured value. So when the configured threshold doubled, the internal limiter's fraction stayed pinned to the old MAX, and ALL inbound auth requests started getting throttled at the internal limiter. Auth fails → API fails → 502s everywhere.

Took us some time to figure out because the symptoms looked like an upstream load balancer issue (502s typically point that direction) and our first hour was spent looking at LB health checks, which were green. Eventually Priya noticed that the auth service's internal metrics dashboard was showing 100% throttle rate on the internal limiter, and we traced it back to the config push. Reverted the change at 18:18 UTC and traffic recovered fully by 18:24.

About 11,400 customer accounts were impacted. Roughly 28 enterprise accounts (the ones with named CSMs) had real revenue impact during their business hours; we know of at least 4 cases where a customer's downstream automation broke and they had to manually clean up. Total inbound support tickets: 217. Refund requests so far: 31 (a few are SLA-credit-only, others are asking for full month credit; legal and finance are working through these case-by-case).

OK, so what should we have done differently, and what are we doing about it.

First, the config push system has no canary deploy for this kind of change. We push global config changes to all auth instances simultaneously. We have canary deploys for code, but not for config. We should fix that. I'd guess 1 sprint of work to add per-region staged config rollout. Pri 1.

Second, the internal limiter shouldn't have a hard-coded MAX disconnected from the global config. That's a code smell that's been there since at least 2024 and we knew about it (I personally was told about it last June by Sarah, who left in September; sorry Sarah, you were right). Need to make the internal limiter compute its fraction against the actual current global config, not against a constant. Probably a 2-week project including the regression tests we need.

Third, the status page issue: we had the status-page check pointing at /healthz on a fixed instance, not at the same endpoints customers hit. So the check stayed green while customers got 502s. Already fixed (Friday evening). Not catching this earlier is partly a process failure — we never had a "would this catch what just happened" review for status-page checks.

Fourth, communication during the incident was not great. We waited 47 minutes from "we know it's an outage" to first proactive customer comms. Some of that was justified (we wanted to know what was happening before broadcasting), some wasn't (we should have at least acknowledged the impact within 15 minutes, even if we didn't have a root cause). Going forward, the on-call commander should issue a "we see it, we're working it" comms within 15 min regardless of root-cause-discovery state.

Fifth, the runbooks didn't have anything on this specific failure mode. To be fair the failure mode was novel — config-push affecting an internal limiter that has its own threshold logic — so I don't think a runbook would have helped much for the diagnosis. But for the response, having a "if 502s are widespread but LB is green, check auth service internal metrics" entry would have shaved 30-40 minutes.

On the customer impact side: we owe the 4 known-broken-downstream customers something more than SLA credits. I'm proposing we do a hands-on data-cleanup support engagement for those 4, free of charge, plus the SLA credit. For the other ~24 enterprise accounts impacted, the standard SLA credit per our MSA is appropriate. For the remaining ~11,400 accounts, the impact was real but bounded (their automation just stalled and resumed when we recovered) — I think a thoughtful customer email + an SLA credit for any account that explicitly requests one is the right move.

There's also a board-level question here — this is the second 4+ hour outage in 2026 (the other was in February with the database storage issue). We're not yet at a level where this rises to a "we need to overhaul our whole reliability program" conversation, but it's the second data point in 90 days, and a third would put us there. I'd flag this in the board prep but not panic the board.

Legal stance: the SLA we sell ("99.9% monthly uptime, with credits for breach") was nominally violated for the affected accounts; we should not contest credit requests where the SLA was clearly breached. For the no-impact accounts that are nonetheless asking for credits because they "lost trust" — that's a relationship call, not a contractual one, and finance/CS should handle case-by-case.

OK, I think that's everything. We should probably loop the eng team on the technical postmortem (separately, with the actual log timelines), and I'll draft a customer-facing version for the comms team to send Monday. The legal team needs the SLA-impact analysis by EOD Tuesday for the credit-processing batch.

Let me know if I missed anything important. — M.
