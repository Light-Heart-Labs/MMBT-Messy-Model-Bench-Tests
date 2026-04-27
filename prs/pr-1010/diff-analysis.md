# PR #1010 Diff Analysis

## Claimed Change

chore(schema): mark provider API keys as secret in .env.schema.json

## Actual Change Characterization

Schema secret flips are correct and covered. Targeted pytest for all five provider-key flags passes 5/5. This also complements, but does not replace, the broader jq-absent masking gap found earlier in #994.

## Surface Area

- Subsystems: dashboard-api
- Changed files: 2
- Additions/deletions: +39 / -5

## Fit Assessment

The change is small or well-contained enough for merge after CI.
