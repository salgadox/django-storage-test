terraform {
  cloud {
    organization = "exaf-epfl"
    workspaces {
      name = "django-storage-test-meta"
    }
  }
}
