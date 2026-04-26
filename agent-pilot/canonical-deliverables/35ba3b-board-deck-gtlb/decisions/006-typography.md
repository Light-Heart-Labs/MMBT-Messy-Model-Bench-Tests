# ADR-006: Typography — System Sans-Serif Over Custom Fonts

**Date:** 2026-04-26
**Status:** Accepted

## Context
The deck needs typography that is clean, modern, and reproducible. The question is whether to use custom fonts (Inter, Roboto) or system fonts.

## Decision
**Use system sans-serif fonts (Helvetica Neue, Arial, sans-serif) for all text.**

## Rationale
1. **Reproducibility** — System fonts are available on every machine. Custom fonts require embedding, which can cause rendering issues across different PowerPoint versions.
2. **Clean and modern** — Helvetica Neue is the gold standard for clean, modern typography. It's used by Apple, Airbnb, and many other tech companies.
3. **No font licensing issues** — Custom fonts may have licensing restrictions. System fonts are free to use.
4. **Consistent rendering** — System fonts render consistently across different operating systems and PowerPoint versions.

## Alternatives Considered
- **Inter:** Rejected — requires embedding, not available on all systems.
- **Roboto:** Rejected — same issue as Inter.
- **Georgia (serif):** Rejected — serif fonts feel traditional, not modern. The deck should feel contemporary.

## Consequences
- All text uses Helvetica Neue (Mac) / Arial (Windows) / sans-serif (fallback).
- Numbers use monospace (Menlo / Consolas / monospace) for alignment.
- Headings are bold, body is regular.
