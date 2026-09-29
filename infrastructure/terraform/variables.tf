variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
  default     = "global-life-event-ai-prod"
}

variable "region" {
  type        = string
  description = "Google Cloud Region"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Deployment environment (prod, staging, dev)"
  default     = "prod"
}
