terraform {
  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = "1.2.0"
    }
  }
}

# PC information
provider "nutanix" {
  username     = var.user
  password     = var.password
  endpoint     = var.endpoint
  insecure     = true
  wait_timeout = 60
}

data "nutanix_cluster" "cluster" {
  name = var.cluster_name
}

resource "nutanix_subnet" "subnet" {
  # Cluster will this VLAN live on
  cluster_uuid = data.nutanix_cluster.cluster.id

  # General Information
  name        = var.subnet_name
  vlan_id     = var.subnet_vlan
  subnet_type = "VLAN"

  # Managed L3 Networks. Turn on IPAM
  prefix_length                = var.subnet_prefix
  default_gateway_ip           = var.subnet_gw
  subnet_ip                    = var.subnet_ip
  ip_config_pool_list_ranges   = var.subnet_pool
  dhcp_domain_name_server_list = var.subnet_dns
}

resource "nutanix_image" "image" {
  name        = var.image_name
  description = var.image_description
  source_uri  = var.image_source_uri
  lifecycle {
    prevent_destroy = true
  }
}

# InfluxDB VM
resource "nutanix_virtual_machine" "influxdb_vm" {
  name                                     = var.influxdb_vm_name
  description                              = var.influxdb_vm_description
  cluster_uuid                             = data.nutanix_cluster.cluster.id
  num_vcpus_per_socket                     = var.influxdb_vm_vcpus
  num_sockets                              = var.influxdb_vm_sockets
  memory_size_mib                          = var.influxdb_vm_memory
  guest_customization_cloud_init_user_data = filebase64(var.vm_customization)

  disk_list {
    data_source_reference = {
      kind = "image"
      uuid = nutanix_image.image.id
    }
  }

  nic_list {
    subnet_uuid = nutanix_subnet.subnet.id
  }
}

# Test VMs
resource "nutanix_virtual_machine" "test_vms" {
  count                                    = var.test_vm_count
  name                                     = format("%s-%02s", var.test_vm_name_prefix, count.index)
  description                              = var.test_vm_description
  cluster_uuid                             = data.nutanix_cluster.cluster.id
  num_vcpus_per_socket                     = var.test_vm_vcpus
  num_sockets                              = var.test_vm_sockets
  memory_size_mib                          = var.test_vm_memory
  guest_customization_cloud_init_user_data = filebase64(var.vm_customization)

  disk_list {
    data_source_reference = {
      kind = "image"
      uuid = nutanix_image.image.id
    }
  }

  nic_list {
    subnet_uuid = nutanix_subnet.subnet.id
  }
}

locals {
  test_vm_dict = {
    for vm in nutanix_virtual_machine.test_vms :
    vm.name => vm.nic_list[0].ip_endpoint_list[0].ip
  }
}

resource "time_sleep" "wait_30_seconds" {
  depends_on      = [nutanix_virtual_machine.test_vms, nutanix_virtual_machine.influxdb_vm]
  create_duration = "30s"
}

resource "local_file" "ansible_inventory" {
  depends_on = [time_sleep.wait_30_seconds]

  content = templatefile("ansible_inventory.tftpl",
    {
      influxdb_vm_name = var.influxdb_vm_name
      influxdb_vm_ip   = nutanix_virtual_machine.influxdb_vm.nic_list[0].ip_endpoint_list[0].ip
      test_group_name  = var.test_vm_name_prefix
      test_vms         = local.test_vm_dict
    }
  )
  filename = var.ansible_inventory

  provisioner "local-exec" { command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -u ansible -i '${var.ansible_inventory}' ../ansible/playbooks/influxdb.yml" }
  # provisioner "local-exec" {command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -u ansible -i '${var.ansible_inventory}' ../ansible/playbooks/test_afs.yml"}
}
