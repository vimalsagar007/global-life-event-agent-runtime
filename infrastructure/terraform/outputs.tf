output "cloud_run_url" {
  description = "URL of deployed Global Life Event AI Cloud Run Service"
  value       = google_cloud_run_v2_service.app_service.uri
}

output "firestore_database" {
  description = "Firestore Native Database"
  value       = google_firestore_database.database.name
}

output "pubsub_topic" {
  description = "Pub/Sub Topic for Event-Driven Re-planning"
  value       = google_pubsub_topic.event_topic.name
}

output "bigquery_dataset" {
  description = "BigQuery Dataset for Analytics"
  value       = google_bigquery_dataset.analytics.dataset_id
}
