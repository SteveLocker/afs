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

resource "nutanix_virtual_machine" "vm" {
  count                = var.vm_count
  name                 = "${format("%s-%02s", var.vm_name_prefix, count.index)}"
  description          = var.vm_description
  cluster_uuid         = data.nutanix_cluster.cluster.id
  num_vcpus_per_socket = var.vm_vcpus
  num_sockets          = var.vm_sockets
  memory_size_mib      = var.vm_memory
  guest_customization_cloud_init_user_data  = filebase64(var.vm_customization)
  
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

resource "time_sleep" "wait_30_seconds" {
  depends_on = [nutanix_virtual_machine.vm]

  create_duration = "30s"
}

resource "local_file" "ansible_inventory" {
  depends_on = [time_sleep.wait_30_seconds]
  content = templatefile("ansible_inventory.tftpl",
    {
      group_name = var.vm_name_prefix
      vm_ips = nutanix_virtual_machine.vm[*].nic_list[0].ip_endpoint_list[0].ip
    }
  )
  filename = var.ansible_inventory

  # provisioner "local-exec" {command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -u ansible -i '${var.ansible_inventory}' ../ansible/test_afs.yml"}
}
