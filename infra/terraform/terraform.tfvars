# Endpoint variables (Prism Central)
endpoint     = "10.66.39.99"
cluster_name = "FatalFrame"

# Subnet variables
subnet_name   = "ipam"
subnet_vlan   = "0"
subnet_prefix = "22"
subnet_ip     = "10.66.36.0"
subnet_gw     = "10.66.36.1"
subnet_dns    = ["10.66.40.5"]
subnet_pool   = ["10.66.39.200 10.66.39.250"]

# Image variables
image_name        = "Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"
image_description = "Rocky 9 cloud image"
image_source_uri  = "https://dl.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"

# Cloud init variables
vm_customization = "../cloudinit/init.yml"

# InfluxDB VM
influxdb_vm_name        = "influxdb"
influxdb_vm_description = "harold.gutierrez@nutanix.com"
influxdb_vm_vcpus       = "8"
influxdb_vm_sockets     = "1"
influxdb_vm_memory      = "4096"

# Test VMs variables
test_vm_count       = "3"
test_vm_name_prefix = "test"
test_vm_description = "harold.gutierrez@nutanix.com"
test_vm_vcpus       = "1"
test_vm_sockets     = "1"
test_vm_memory      = "2048"

# Ansible variables
ansible_inventory = "../ansible/inventory/hosts"
