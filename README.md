# HabotConnect Hiring Project — Junior Cloud & DevOps Engineer (GCP / Django / React)

**Candidate Name:** Kolla Hema Sundharam
**Contact Email:** kollahemasundharam.tech9@gmail.com
**Contact Phone:** +91 9505005629
**Submission Date:** 02-08-2026
**Repository:** https://github.com/hemasundharGit/Habot-Combat

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
   that blocks any commit containing lint violations, Terraform formatting
   errors, or hardcoded secrets.
3. **Schema Mapping and DCYN Validation (Django REST Framework)** — a
   serializer that converts an incoming student-onboarding JSON payload into
   strict binary Yes/No fields, removing ambiguity and the need for human
   judgment.

## Folder Structure

```
Habot-Combat/
├── README.md
├── planted-secret-demo.py
├── .github/
│   └── workflows/
│       └── build-gate.yml
├── terraform/
│   ├── main.tf
│   ├── terraform.tfvars.example
│   └── .gitignore
├── django/
│   └── serializers.py
├── data-mapping/
│   ├── schema-mapping.csv
│   └── schema-mapping.xlsx
└── presentation/
    └── HabotConnect_Hiring_Project_Presentation.pptx
```

> **Note:** the CI/CD workflow lives at the repository-root-relative path
> `.github/workflows/build-gate.yml`, which is the only location GitHub
> Actions will detect and run. An earlier draft of this repo mistakenly
> nested it under `ci-cd/.github/workflows/`, where it was invisible to
> GitHub Actions — that has since been corrected.

## How to Review

- **Terraform:** `terraform/main.tf` — see inline comments explaining each
  Least Privilege / IAM design decision. `terraform.tfvars.example` shows the
  expected variable structure without exposing real project values.
- **CI/CD Gate:** `.github/workflows/build-gate.yml` — this workflow runs on
  every push and pull request. It is configured as a required status check
  in branch protection, so it fails closed (blocks merge) on lint errors,
  Terraform formatting/validation errors, or detected secrets. See
  `planted-secret-demo.py` and the Fail-Closed Proof slide in the
  presentation for a live demonstration of the gate blocking an insecure
  commit.
- **Schema Validation:** `django/serializers.py` — see the
  `DCYNStudentOnboardingSerializer` class and its field-level validators.
- **Schema Mapping:** `data-mapping/schema-mapping.csv` and
  `schema-mapping.xlsx` (Wrap Text enabled per submission requirements) —
  map raw incoming JSON fields to their DCYN binary equivalents and their
  BigQuery destination columns.
- **Presentation:** `presentation/HabotConnect_Hiring_Project_Presentation.pptx`
  — architectural overview, logic flow, and fail-closed demonstration.

## Assumptions Made

- Assumed the pipeline service account already exists and is referenced by
  variable (`pipeline_service_account_email`) rather than created within
  this Terraform module, to keep IAM bootstrapping separate from resource
  provisioning.
- The Row Access Policy uses the native `google_bigquery_row_access_policy`
  Terraform resource; if a deployed provider version lacks support for it,
  the equivalent SQL is intended to be applied manually and documented
  alongside this README rather than silently omitted.
- The 30-day lifecycle deletion rule on the D0 Raw Landing bucket assumes
  staged data is durably persisted into D1 well before that window closes.
- Analyst group access to D1 is read-only and row-restricted by consent
  status; no analyst identity is granted write access under any
  configuration.

## Current Status

- [x] Terraform staging provisioning (`terraform/main.tf`)
- [x] Poka-Yoke CI/CD workflow authored and corrected to the proper
      `.github/workflows/` path
- [x] Django DCYN serializer (`django/serializers.py`)
- [x] Schema mapping spreadsheet with Wrap Text enabled
- [x] Presentation deck drafted
- [ ] All three build-gate checks passing green on `main`
- [ ] Fail-closed demo executed on a throwaway branch with screenshots
      captured
- [ ] Branch protection enabled with the build gate as a required check
- [ ] Screenshots inserted into the presentation deck
- [ ] Final review for leftover placeholders before submission
