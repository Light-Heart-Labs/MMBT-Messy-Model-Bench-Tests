You have access to a fictional SaaS product's overflowing support inbox at `/input/repo/tickets.txt` — 30 unread tickets in plain-text format with `=== TICKET NNN ===` separators, each having `From:`, `Subject:`, and `Body:`. Some are real product issues; some are spam, phishing, or off-topic.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit.

Your task: **triage the 30 tickets.** For each ticket, classify it into one of these categories and assign an urgency level. Identify duplicates / follow-ups that refer to the same underlying issue. Produce a structured JSON output a human triager would actually find useful.

## Categories (closed vocabulary — pick exactly one per ticket)

- `bug-report` — concrete reproducible product bug
- `billing-refund` — explicit refund or credit ask
- `billing-other` — billing question that isn't a refund (invoice, plan change inquiry, tax question)
- `feature-request` — wants something the product doesn't currently do
- `incident-active` — something's actively broken right now and impact is ongoing
- `account-management` — seat add/remove, cancellation, admin changes
- `auth-permissions` — login issues, sharing/permission problems, role-based access
- `general-question` — non-urgent how-do-I, onboarding, pricing inquiry
- `spam-or-noise` — phishing, marketing pitches with no substance, obviously fictitious requests
- `security-incident` — customer-reported security issue (account compromise, extortion, vuln disclosure)
- `external-business` — partnerships, sales, M&A, podcast pitches; not customer support per se
- `legal-compliance` — GDPR/CCPA data requests, subpoenas, regulatory

## Urgency (closed vocabulary)

- `urgent` — production-down, security-incident-active, time-sensitive deadline
- `normal` — needs response within ~1 business day, no smoking-gun
- `low` — can be batched, not blocking
- `n/a` — for noise/spam where urgency doesn't apply

## Required output

A single file at `/workspace/triage_results.json` with this exact shape:

```json
{
  "tickets": {
    "001": {
      "category": "<one of the 12 categories>",
      "urgency": "<one of urgent|normal|low|n/a>",
      "duplicate_of": null
    },
    "002": {
      "category": "...",
      "urgency": "...",
      "duplicate_of": null
    }
  },
  "summary": {
    "by_category": {"bug-report": <count>, "billing-refund": <count>, ...},
    "urgent_count": <int>,
    "duplicate_clusters": [["001", "011"], ["014", "023", "030"]]
  },
  "notes": "Optional free text — anything you want a human reviewer to know about ambiguous calls."
}
```

The `duplicate_of` field is the lower-numbered ticket ID a follow-up refers to (e.g., `"030"` has `"duplicate_of": "014"`). For the original ticket of a cluster, leave `duplicate_of: null`. Each duplicate cluster appears once in `duplicate_clusters` as a sorted list of all ticket IDs in the cluster.

Beyond the JSON, you may produce ADRs in `/workspace/decisions/` for non-obvious calls, and a brief summary at `/workspace/README.md` explaining your overall approach and any tickets you're unsure about.

## Rules of the road

- **Read every ticket before deciding categories.** Don't classify in order — context from later tickets sometimes resolves earlier ambiguity.
- **The closed vocabulary is fixed.** Don't invent new categories. If a ticket really doesn't fit, pick the closest one and explain in `notes`.
- **Duplicate clusters need explicit detection.** Two reports of the same underlying issue from the same org, or follow-ups to a prior ticket from the same sender, are duplicates. Note them in `duplicate_of` and in `duplicate_clusters`.
- **Don't fabricate.** If you can't determine urgency from the ticket text, mark it `normal` and explain. Don't invent SLA breaches the customer didn't mention.
- **Be skeptical of obvious noise.** Phishing emails impersonating "Account Security Team," extortion threats, fictitious-premise requests ("free collectables"), affiliate-link spam — these are `spam-or-noise`, not real categories.

## Output

A reviewer with 10 minutes should be able to read your `triage_results.json` plus your `README.md` and start working through the tickets in your recommended urgency order without re-reading the originals.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Do not ask for clarification — make reasonable choices and document them in `/workspace/decisions/` or in the JSON's `notes` field.
