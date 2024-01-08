# Configure GCP provider
provider "google" {
  project = "ml-demo-384110"
  region  = "europe-west1" # Change this to your desired region
}

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 3.0"
    }
  }
}



resource "google_cloudbuild_trigger" "trigger" {
  name = "my-trigger"
  event_type = "google.storage.object.finalize"
  resource = "gs://my-bucket/*"
  action {
    type = "BUILD"
    build {
      source {
        repo_source {
          project_id = var.project_id
          repo_name = var.repo_name
          branch_name = var.branch_name
        }
      }
      steps {
        name = "gcr.io/cloud-builders/docker"
        args = ["build", "-t", "gcr.io/my-project/my-image", "."]
      }
      images = ["gcr.io/my-project/my-image"]
    }
  }
}