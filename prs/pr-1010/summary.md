# PR #1010 Summary

## Claim In Plain English

chore(schema): mark provider API keys as secret in .env.schema.json

## Audit Restatement

Schema secret flips are correct and covered. Targeted pytest for all five provider-key flags passes 5/5. This also complements, but does not replace, the broader jq-absent masking gap found earlier in #994.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: chore/schema-secret-flip
- Changed files: 2
- Additions/deletions: +39 / -5
- Labels: none
