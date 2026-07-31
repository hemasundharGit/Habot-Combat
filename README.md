# HabotConnect Hiring Project — Junior Cloud & DevOps Engineer (GCP / Django / React)

**Candidate Name:** Kolla Hema Sundharam
**Contact Email:** kollahemasundharam.tech9@gmail.com
**Contact Phone:** [YOUR PHONE NUMBER]
**Submission Date:** [DATE]

---

## Project Overview

This repository contains the completed Hiring Project deliverables for the Junior
Cloud & DevOps Engineer position at HabotConnect. It addresses the staging
incident scenario described in the project brief: unencrypted API credentials
committed to application code, and a downstream database schema mismatch
breaking analytics.

The submission restores system integrity through three components:

1. **Infrastructure as Code (Terraform)** — secure provisioning of a raw
   landing bucket and a staged/enforced BigQuery dataset, with strict IAM and
   Row-Level Security.
2. **Poka-Yoke CI/CD Build Gate (GitHub Actions)** — a fail-closed pipeline
   that blocks any commit containing lint violations or hardcoded secrets.
3. **Schema Mapping and DCYN Validation (Django REST Framework)** — a
   serializer that converts an incoming student-onboarding JSON payload into
   strict binary Yes/No fields, removing ambiguity and the need for human
   judgment.

## Folder Structure

```
habot-project/
├── README.md
├── terraform/
│   └── main.tf
├── ci-cd/
│   └── .github/workflows/build-gate.yml
├── django/
│   └── serializers.py
└── data-mapping/
    └── schema-mapping.csv
```

## How to Review

- **Terraform:** `terraform/main.tf` — see inline comments explaining each
  Least Privilege / IAM design decision.
- **CI/CD Gate:** `ci-cd/.github/workflows/build-gate.yml` — this workflow is
  configured as a required check; it fails closed (blocks merge) on lint
  errors or detected secrets. A screenshot of a blocked build using a
  deliberately planted fake credential is included in the presentation deck.
- **Schema Validation:** `django/serializers.py` — see the `DCYNStudentOnboardingSerializer`
  class and its field-level validators.
- **Schema Mapping:** `data-mapping/schema-mapping.csv` — maps raw incoming
  JSON fields to their DCYN binary equivalents and their BigQuery destination
  columns. (Submitted separately as an .xlsx with Wrap Text enabled per
  submission requirements.)

## Assumptions Made

- [List any assumptions you made, e.g., "Assumed the service account running
  the pipeline already exists and is referenced by variable, not hardcoded."]
- [Add 2-3 more as needed — the panel wants to see you think in explicit,
  stated assumptions rather than silent guesses.]
