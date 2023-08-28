# TODO: fix error on cycle
# ! "Error: Cycle: module.stu-linux.null_resource.ansible_provisioner, module.stu-linux.azurerm_virtual_machine.vm"
resource "null_resource" "ansible_provisioner" {
  provisioner "local-exec" {
    command = "ansible-playbook -i '${azurerm_public_ip.vm.ip_address},' playbook.yml"
    working_dir = "${path.module}/ansible"
  }

  depends_on = [
    azurerm_public_ip.vm,
    azurerm_network_interface.vm,
    azurerm_virtual_machine.vm,
  ]
}

resource "azurerm_public_ip" "vm" {
  name                = "public-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Dynamic"
}

resource "azurerm_network_interface" "vm" {
  name                = "nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "ipconfig"
    subnet_id                     = var.subnet_id
    public_ip_address_id          = azurerm_public_ip.vm.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_machine" "vm" {
  name                  = "vm"
  location              = var.location
  resource_group_name   = var.resource_group_name
  network_interface_ids = [azurerm_network_interface.vm.id]
  vm_size               = var.vm_size

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "22.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "osdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "vm"
    admin_username = var.admin_username
    admin_password = var.admin_password
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  depends_on = [
    null_resource.ansible_provisioner,
  ]
}
