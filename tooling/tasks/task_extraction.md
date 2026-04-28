You have access to an earnings press release at `/input/repo/press_release.txt` from a fictional public company. You also have a JSON schema definition at `/input/repo/schema.json` listing the exact fields to extract.

You have a fresh Linux VM with Python 3.11 and standard CLI tools. No time limit.

Your task: **extract every field listed in the schema from the press release**, and produce a single JSON file at `/workspace/extraction_results.json` with this exact shape:

```json
{
  "fields": {
    "<field_name>": <value>,
    "<field_name>": <value>,
    ...
  },
  "uncertain": ["<field_name>", ...],
  "notes": "Optional free text — anything you want to flag"
}
```

The schema lists 20 fields. Each field has:
- a `type` (`number`, `integer`, `string`, or `date`)
- a `notes` field with hints about acceptable variants where ambiguity might arise
- `units` where the value carries them (the answer must be in the documented units)

## Rules of the road

- **Match the units exactly.** If a field is `units: "USD millions"`, the answer must be in millions of dollars (e.g., `187.4`, not `187400000` and not `0.1874`). The press release may use mixed conventions; convert to the documented units.
- **Match the type exactly.** `integer` fields must be JSON integers (no decimal point). `date` fields must be ISO 8601 (`YYYY-MM-DD`). `number` fields are JSON numbers.
- **No fabrication.** If a field is genuinely not in the press release, set its value to `null` and add it to the `uncertain` array. Don't guess. Don't infer values from boilerplate.
- **Be precise on totals.** If a number is "approximately $115 million," extract `115` (the press release's stated figure), not your own back-calculation. Defer to the document's own statement.
- **Don't extract from forward-looking statements.** Guidance fields (`fy2026_revenue_guidance_low_*`, etc.) are explicitly listed and ARE expected. But don't pull other speculative numbers from the FLS section.
- **Watch for sign and direction.** `gaap_operating_loss` would be negative if asked, but the schema asks for `non_gaap_operating_income_usd_millions` (positive), not loss. Read the field name carefully.

## Output

Write `/workspace/extraction_results.json` with the schema above. You may also produce a `/workspace/notes.md` documenting any judgment calls or ambiguities, and a `/workspace/decisions/` directory with ADRs for non-obvious extraction choices.

When you're done, the final commit tags a release.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Do not ask for clarification — make reasonable choices and document them.
