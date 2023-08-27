resource "azurerm_resource_group" "stu" {
  name     = local.resource_group_name
  location = "regionalregion"
}

module "stu-network" {
  source              = "./modules/network"
  prefix               = "stu"
  resource_group_name = azurerm_resource_group.stu.name
  location            = azurerm_resource_group.stu.location
}

module "stu-DC" {
  source                        = "./modules/active-directory"
  resource_group_name           = azurerm_resource_group.stu.name
  location                      = azurerm_resource_group.stu.location
  prefix                         = "stu"
  subnet_id                     = module.stu-network.domain_subnet_id
  active_directory_domain       = local.master_domain
  active_directory_netbios_name = "labs"
  admin_username                = local.master_admin_username
  admin_password                = local.master_admin_password
}

module "stu-client" {
  source                    = "./modules/windows-client1"
  resource_group_name       = azurerm_resource_group.stu.name
  location                  = azurerm_resource_group.stu.location
  prefix                     = "stu"
  subnet_id                 = module.stu-network.domain_clients_subnet_id
  active_directory_domain   = local.master_domain
  active_directory_username = local.master_admin_username
  active_directory_password = local.master_admin_password
  admin_username            = local.master_admin_username
  admin_password            = local.master_admin_password
  networksec_group          = azurerm_network_security_group.stu-rdp.id
}

output "stu_Public_IP" {
  value = module.stu-client.public_ip_address
}

module "stu-linux" {
  source                    = "./modules/linux"
  resource_group_name       = azurerm_resource_group.stu.name
  location                  = azurerm_resource_group.stu.location
  prefix                     = "stu"
  subnet_id                 = module.stu-network.domain_subnet_id
  active_directory_domain   = local.master_domain
  active_directory_username = local.master_admin_username
  active_directory_password = local.master_admin_password
  admin_username            = local.master_admin_username
  admin_password            = local.master_admin_password
}

resource "azurerm_network_security_group" "stu-rdp" {
  name                = "stu-rdp"
  resource_group_name = azurerm_resource_group.stu.name
  location            = "regionalregion"

  security_rule {
    name                       = "stu-rdp-rule-mgmt"
    direction                  = "Inbound"
    access                     = "Allow"
    priority                   = 200
    source_address_prefix       = "mgmtip"
    source_port_range          = "*"
    destination_address_prefix  = "*"
    destination_port_range     = "3389"
    protocol                   = "TCP"
  }

  security_rule {
    name                       = "stu-internal-in"
    direction                  = "Inbound"
    access                     = "Allow"
    priority                   = 300
    source_address_prefix       = "10.10.0.0/16"
    source_port_range          = "*"
    destination_address_prefix  = "*"
    destination_port_range     = "*"
    protocol                   = "*"
  }

  security_rule {
    name                       = "stu-internal-out"
    direction                  = "Outbound"
    access                     = "Allow"
    priority                   = 400
    source_address_prefix       = "10.10.0.0/16"
    source_port_range          = "*"
    destination_address_prefix  = "*"
    destination_port_range     = "*"
    protocol                   = "*"
  }
}
