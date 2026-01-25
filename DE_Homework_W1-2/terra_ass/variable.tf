variable "credentials_file_path" {
  default     = "./keys/teraform-mar-d29601022ad5.json"
  description = "Path to the GCP credentials JSON file"
}



variable "big_data_name" {
  default     = "demo_dataset"
  description = "My big query dataset name"
}

variable "gcs_storage_class" {
  default     = "STANDARD"
  description = "My storage bucket class"
}

variable "gcs_location" {
  default     = "US"
  description = "My storage bucket location"
}

variable "gcs_bucket_name" {
  default     = "teraform-mar-terra-bucket"
  description = "My storage bucket name"
}