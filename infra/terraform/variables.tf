# Endpoint variables
variable "endpoint" {
  type = string
}
variable "cluster_name" {
  type = string
}
variable "user" {
  type = string
}
variable "password" {
  type = string
}

# Subnet variables
variable "subnet_name" {
  type = string
}
variable "subnet_vlan" {
  type = string
}
variable "subnet_prefix" {
  type = string
}
variable "subnet_ip" {
  type = string
}
variable "subnet_gw" {
  type = string
}
variable "subnet_dns" {
  type = list(any)
}
variable "subnet_pool" {
  type = list(any)
}

# Image variables
variable "image_name" {
  type = string
}
variable "image_description" {
  type = string
}
variable "image_source_uri" {
  type = string
}

# InfluxDB VMs variables
variable "influxdb_vm_name" {
  type = string
}
variable "influxdb_vm_description" {
  type = string
}
variable "influxdb_vm_vcpus" {
  type = string
}
variable "influxdb_vm_sockets" {
  type = string
}
variable "influxdb_vm_memory" {
  type = number
}


# Frontend VMs variables
variable "frontend_vm_name" {
  type = string
}
variable "frontend_vm_description" {
  type = string
}
variable "frontend_vm_vcpus" {
  type = string
}
variable "frontend_vm_sockets" {
  type = string
}
variable "frontend_vm_memory" {
  type = number
}


# Worker VMs variables
variable "worker_vm_name" {
  type = string
}
variable "worker_vm_description" {
  type = string
}
variable "worker_vm_vcpus" {
  type = string
}
variable "worker_vm_sockets" {
  type = string
}
variable "worker_vm_memory" {
  type = number
}


# Test VMs variables
variable "test_vm_count" {
  type = number
}
variable "test_vm_name_prefix" {
  type = string
}
variable "test_vm_description" {
  type = string
}
variable "test_vm_vcpus" {
  type = string
}
variable "test_vm_sockets" {
  type = string
}
variable "test_vm_memory" {
  type = number
}

# Cloud-init variables
variable "vm_customization" {
  type = string
}

# Ansible variables
variable "ansible_inventory" {
  type = string
}
