terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials_file_path)
  project     = "teraform-mar"
  region      = "us-central1"
}


resource "google_storage_bucket" "auto-expire" {
  name          = var.gcs_bucket_name
  location      = var.gcs_location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo-dataset" {
  dataset_id = "demo_dataset_mar"
}