terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.20.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Service Accounts
resource "google_service_account" "orchestrator_sa" {
  account_id   = "life-event-orchestrator-sa"
  display_name = "Global Life Event AI Orchestrator Service Account"
}

# Cloud Run Service for FastAPI Backend & Frontend
resource "google_cloud_run_v2_service" "app_service" {
  name     = "global-life-event-app"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.orchestrator_sa.email

    containers {
      image = "gcr.io/${var.project_id}/global-life-event-app:latest"

      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "USE_MOCK_TOOLS"
        value = "true"
      }
      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }
    }
  }
}

# Cloud Run IAM Invoker (Public / Authenticated)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.app_service.location
  name     = google_cloud_run_v2_service.app_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Firestore Database for Operational State
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Pub/Sub Topic for Event-Driven Re-planning
resource "google_pubsub_topic" "event_topic" {
  name = "life-event-notifications"
}

resource "google_pubsub_subscription" "replanning_sub" {
  name  = "replanning-agent-sub"
  topic = google_pubsub_topic.event_topic.name

  ack_deadline_seconds = 20
}

# BigQuery Dataset for Analytics & Trace Logging
resource "google_bigquery_dataset" "analytics" {
  dataset_id  = "life_event_analytics"
  description = "Global Life Event AI Execution Analytics"
  location    = var.region
}

# Storage Bucket for Uploaded Documents
resource "google_storage_bucket" "documents_bucket" {
  name                     = "${var.project_id}-user-documents"
  location                 = var.region
  force_destroy            = true
  public_access_prevention = "enforced"
}
