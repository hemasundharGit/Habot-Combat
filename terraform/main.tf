# =============================================================================
# HabotConnect — Secure Staging Provisioning (Task 1)
# Candidate: Kolla Hema Sundharam | Contact: kollahemasundharam.tech9@gmail.com
#
# Provisions:
#   - D0 Raw Landing: a GCS bucket for raw, untrusted incoming payloads
#   - D1 Staged/Enforced: a BigQuery dataset for validated, schema-enforced data
#
# Design principles applied:
#   - Least Privilege: no broad roles (no roles/owner, no allUsers)
#   - Defense in depth: bucket-level access control + dataset-level IAM +
#     row-level security on top of that
#   - No hardcoded secrets or project-specific literals — everything is a variable
# =============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------------------------------
# Variables — nothing below is hardcoded; all environment-specific values are
# injected at apply time (via terraform.tfvars, CI secrets, or -var flags).
# -----------------------------------------------------------------------------
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "raw_landing_bucket_name" {
  description = "Globally unique name for the D0 Raw Landing bucket"
  type        = string
}

variable "staged_dataset_id" {
  description = "BigQuery dataset ID for D1 Staged/Enforced data"
  type        = string
  default     = "d1_staged_enforced"
}

variable "pipeline_service_account_email" {
  description = "Service account email used by the ingestion pipeline (least-privilege identity, created outside this module)"
  type        = string
}

variable "analyst_group_email" {
  description = "Google Group email for analysts who need read-only access to staged data (row-level restricted)"
  type        = string
}

# -----------------------------------------------------------------------------
# D0 Raw Landing — GCS bucket for unvalidated incoming data
# -----------------------------------------------------------------------------
resource "google_storage_bucket" "raw_landing" {
  name     = var.raw_landing_bucket_name
  project  = var.project_id
  location = var.region

  # Uniform bucket-level access — disables legacy ACLs, forces all access
  # control through IAM only. Required for predictable Least Privilege.
  uniform_bucket_level_access = true

  # Prevent accidental public exposure at the bucket level.
  public_access_prevention = "enforced"

  # Versioning protects against accidental overwrite/deletion of raw payloads
  # — important since this is the only unprocessed copy of incoming data.
  versioning {
    enabled = true
  }

  # Raw landing data is transient by design — auto-delete after 30 days once
  # it has been staged into BigQuery, to control storage cost and blast radius.
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    data_zone = "d0-raw-landing"
    managed_by = "terraform"
  }
}

# Only the pipeline service account may write to raw landing.
# It must NOT have delete/admin rights — object creation only.
resource "google_storage_bucket_iam_member" "raw_landing_writer" {
  bucket = google_storage_bucket.raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.pipeline_service_account_email}"
}

# Pipeline also needs to read back what it just wrote (for the staging step).
resource "google_storage_bucket_iam_member" "raw_landing_reader" {
  bucket = google_storage_bucket.raw_landing.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.pipeline_service_account_email}"
}

# -----------------------------------------------------------------------------
# D1 Staged/Enforced — BigQuery dataset for schema-validated data
# -----------------------------------------------------------------------------
resource "google_bigquery_dataset" "staged_enforced" {
  dataset_id  = var.staged_dataset_id
  project     = var.project_id
  location    = var.region
  description = "D1 Staged/Enforced — schema-validated student onboarding data"

  # Explicit access block replaces default (permissive) dataset ACLs.
  # No "special_group: allAuthenticatedUsers" or "allUsers" entries.
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "WRITER"
    user_by_email = var.pipeline_service_account_email
  }

  access {
    role          = "READER"
    group_by_email = var.analyst_group_email
  }

  delete_contents_on_destroy = false
}

resource "google_bigquery_table" "student_onboarding" {
  dataset_id = google_bigquery_dataset.staged_enforced.dataset_id
  table_id   = "student_onboarding"
  project    = var.project_id

  schema = jsonencode([
    { name = "student_id", type = "STRING", mode = "REQUIRED" },
    { name = "guardian_email", type = "STRING", mode = "REQUIRED" },
    { name = "has_diagnosed_learning_difficulty", type = "BOOLEAN", mode = "REQUIRED" },
    { name = "requires_lsa_support", type = "BOOLEAN", mode = "REQUIRED" },
    { name = "consent_given", type = "BOOLEAN", mode = "REQUIRED" },
    { name = "ingested_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])

  deletion_protection = true
}

# -----------------------------------------------------------------------------
# Row-Level Security (RLS) on the staged table
#
# NOTE: As of the Google provider (~> 5.0), native row-access-policy support
# exists via google_bigquery_row_access_policy. If your provider version does
# not support it, apply the equivalent SQL below manually or via a
# `null_resource` + `gcloud` provisioner, and state that explicitly in your
# submission — do not silently omit RLS.
# -----------------------------------------------------------------------------
resource "google_bigquery_row_access_policy" "analyst_consented_only" {
  project     = var.project_id
  dataset_id  = google_bigquery_dataset.staged_enforced.dataset_id
  table_id    = google_bigquery_table.student_onboarding.table_id
  policy_id   = "analyst_consented_only"

  # Analysts (read-only group) may only see rows where consent was given.
  filter_predicate = "consent_given = true"

  grantees_predefined_expression = "ALLOWED_ALL"
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
output "raw_landing_bucket_url" {
  value = google_storage_bucket.raw_landing.url
}

output "staged_dataset_full_id" {
  value = "${var.project_id}.${google_bigquery_dataset.staged_enforced.dataset_id}"
}
