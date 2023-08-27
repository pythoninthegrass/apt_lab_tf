provider "azurerm" {
  # The "feature" block is required for AzureRM provider 2.x.
  # If you're using version 1.x, the "features" block is not allowed.
  version = "1.27.0"

  subscription_id = "subid"
  client_id       = "clid"
  client_secret   = "clse"
  tenant_id       = "tenid"
}

locals {
  resource_group_name   = "class-resources"
  master_admin_username = "itadmin"
  master_admin_password = "APTClass!"
  master_domain         = "labs.local"
}
