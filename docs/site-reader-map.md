---
title: "Public site reader map"
description: "A routing guide for the public site: what to read first, what is audit evidence, and what is historical."
---

This page explains the site structure. The public site includes both a
reader-facing narrative and the audit trail behind it. Do not start with the
ledgers unless you are auditing provenance.

## Start here

- **Hiring-manager scan**: [`For hiring managers in a hurry`](for-hiring-managers.md) gives the fastest read on what was built, what worked, and what failed.
- **Results-first technical read**: [`Results`](../RESULTS.md) gives the direct-detection and OOD-generalization findings before the methodology details.
- **Full narrative**: [`WRITEUP`](../WRITEUP.md) is the hub for the complete technical story.
- **Repository scan**: [`README`](../README.md) is the GitHub-front-door version of the same story.

## Evidence and audit trail

- **Evidence ledger**: [`EVIDENCE`](../EVIDENCE.md) tracks external evidence used in claims.
- **Spec lock sheet**: [`SPEC_SHEET`](../SPEC_SHEET.md) is the historical Phase-0 fill-in sheet. It is useful for auditing how decisions were locked, not for a first read.
- **Submission audit ledger**: [`SUBMISSION_AUDIT`](../SUBMISSION_AUDIT.md) is generated from ADR frontmatter. It proves that claims have decision records.
- **Assumptions registry**: [`assumptions`](../assumptions.md) records load-bearing assumptions and their current interpretation.
- **Carryforward log**: [`NEXT_STEPS`](../NEXT_STEPS.md) separates completed carryforward work from actual future directions.

## Historical decisions

The [`decisions`](../decisions/README.md) section contains immutable ADRs. Read
the index first. Individual ADRs are historical records: later patches clarify
the current state around them instead of rewriting their original decision
content.

## Static analysis appendices

The notebook pages are frozen, rendered HTML appendices. They are there for
inspection and reproducibility context; they are not interactive notebooks on
the live site.
