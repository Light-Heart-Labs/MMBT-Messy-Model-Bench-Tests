# Project Aurora — meeting notes log

## 2026-03-04 (Tue) — Aurora kickoff

Folks present: Sara (PM), Marcus (TL), Jen (UX), Roman (data), Brendan (CEO, briefly)

- Brendan dropped by for first 10 min: "I want this in customers' hands by end of June." Kicked it back to us for a real plan.
- Sara: Aurora is the new dashboard refresh + the embedded analytics SDK. We've been calling them separate but they're really one shipped thing because the SDK uses the new dashboard primitives.
- Marcus: backend is ready-ish. The query layer needs work to support the SDK's filter expressions. Estimate 4-6 weeks for that.
- Jen: design is in progress. Two big open questions — does the dashboard support custom branding for customers using the SDK (no current answer), and what's the mobile story (also no current answer).
- Roman: data pipeline is fine for the dashboard. Concerns about latency for the SDK if customers use it with 100+ panels per page — current arch assumes <20.
- Action: Sara to draft scope doc by Friday. Marcus to size the query-layer work properly. Jen to come back with branding answer next week. Roman to investigate panel-density limits.

## 2026-03-11 (Tue) — week 2

Folks: Sara, Marcus, Jen, Roman.

- Sara shared scope doc; got light pushback. Marcus thinks scope is too aggressive for end-of-June.
- Jen brought back the custom-branding answer: yes we want to support it; she has mockups; it's another ~3 weeks of design work she didn't budget for.
- Roman: panel-density issue is real; current arch hits ~40 panels/page before lag is unacceptable. Architectural fix needed.
- Marcus's revised estimate for the query-layer work: 8 weeks not 4-6. Reasons: the SDK filter expressions need a parser they don't currently have, and supporting filter combinations is non-trivial.
- Sara: this changes timeline math. End-of-June is not realistic. Need to talk to Brendan.
- Action: Sara to brief Brendan this week and come back with a renegotiated date.

## 2026-03-18 (Tue) — week 3

Folks: Sara, Marcus, Jen, Roman. Brendan briefly via Zoom.

- Brendan dialed in: "I hear you on the timeline. Worst case I can defend mid-July to the board, but August is a real problem because of the customer commit we made at the conference."
- Sara: walked through the revised plan. End-of-July GA is reachable IF we cut custom-branding from V1 and IF we accept the 40-panel-per-page limit as a known limitation in V1.
- Brendan: "Cut custom-branding for V1. Document the panel limit but make sure the docs are clear on it."
- Jen: OK to defer custom-branding. She will pivot her remaining capacity to mobile, which is the bigger UX gap.
- Roman: 40-panel-limit is OK to ship if documented; will continue work on the architectural fix as a fast-follow for V1.1 in August/September.
- Marcus: query-layer work staying at 8 weeks. He's blocked on a code review from Lin (who's on PTO until 3/24). Needs to escalate to get a substitute reviewer.
- Action: Sara to update the customer-conference commit doc. Marcus to find a sub reviewer this week. Jen to scope mobile.

## 2026-03-25 (Tue) — week 4

Folks: Sara, Marcus, Jen, Roman.

- Marcus: query-layer work moving; got a sub reviewer (Aanya). On track for mid-May completion.
- Jen: mobile scope is bigger than expected. Native iOS + Android would be 12+ weeks minimum. Web-mobile-responsive is 4 weeks. Pushing for responsive + treat native as V2.
- Sara agrees, pushes responsive into V1 plan.
- Roman: started the architectural fix in parallel; estimate 6 weeks.
- Discovered: the embedded SDK has a security model question we didn't address. When customer X embeds a dashboard for their customer Y, what data does Y see? Current assumption is "Y sees what X tells them to see" but we haven't actually built the access-control layer for this. Roman flags this as a blocker for SDK V1.
- Action: Sara to call an emergency security review next week. Marcus to investigate access-control layer effort.

## 2026-04-01 (Tue) — week 5

Folks: Sara, Marcus, Jen, Roman + Priya (security) joined for last 20 min.

- Priya (security): looked at the SDK access-control gap. Says: this is a 4-week minimum project, not a quick fix. Needs proper IAM design + customer-facing API + audit logging. Wants to be in the next planning cycle.
- Marcus: that 4 weeks blows the V1 timeline. We're out of slack.
- Sara: options — (a) ship V1 without the embedded SDK, just the dashboard refresh; SDK becomes V1.5 in August. (b) ship V1 with the SDK but in private-beta only with customers who sign extra contracts about access control. (c) push V1 to August with everything.
- Discussion: Brendan absent today; team can't decide without him. Sara to add to next 1:1 with Brendan.
- Jen: mobile-responsive on track for mid-May.
- Roman: architectural fix on track.
- Action: Sara to escalate access-control timeline question to Brendan. Marcus to start IAM-design conversations with Priya in parallel. Everyone else proceeds with current scope minus SDK access decisions.

## 2026-04-08 (Tue) — week 6 (most recent)

Folks: Sara, Marcus, Jen, Roman.

- Brendan responded on Slack (not in meeting): "Option B — private beta with 3-5 customers. We have access-control commitments to make right but we cannot delay V1 entirely."
- Sara: OK, locking in option B. Need legal involvement for the customer access-control contracts.
- Marcus: query-layer 60% done. Tracking to mid-May. Aanya's reviewing in pace.
- Jen: mobile-responsive is on track. Custom-branding still parked.
- Roman: architectural fix 30% done; on track for V1.1 in August.
- Priya (joined briefly): IAM design started; ready for customer-facing API discussion next week.
- Open issues: legal hasn't responded to private-beta contract draft; one customer (Maevia) was promised general-availability SDK at the conference and they're going to push back when we tell them it's private-beta. Sara has a call with their CSM tomorrow.
- Action: Sara to handle Maevia. Marcus to keep query-layer moving. Roman + Priya to align on IAM API surface.
