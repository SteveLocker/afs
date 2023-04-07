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
  type      = string
}

# Subnet variables
variable "subnet_name" {
  type = string
}
variable subnet_vlan {
  type = string
}
variable subnet_prefix {
  type = string
}
variable subnet_ip {
  type = string
}
variable subnet_gw {
  type = string
}
variable subnet_dns {
  type = list
}
variable subnet_pool {
  type = list
}

# Image variables
variable image_name {
  type = string
}
variable image_description {
  type = string
}
variable image_source_uri {
  type = string
}

# VM variables
variable vm_count {
  type = number
}
variable vm_name_prefix {
  type = string
}
variable vm_description {
  type = string
}
variable vm_vcpus {
  type = string
}
variable vm_sockets {
  type = string
}
variable vm_memory {
  type = number
}
variable vm_customization {
  type = string
}

# Ansible variables
variable ansible_inventory {
  type = string
}