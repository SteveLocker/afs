# Endpoint variables (Prism Central)
endpoint     = "10.24.139.59"
cluster_name = "MarbleMadness"

# Subnet variables
subnet_name    = "ipam"
subnet_vlan    = "0"
subnet_prefix  = "22"
subnet_ip      = "10.24.136.0"
subnet_gw      = "10.24.136.1"
subnet_dns     = ["10.66.40.5"]
subnet_pool = ["10.24.139.120 10.24.139.153"]

# Image variables
image_name        = "Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"
image_description = "Rocky 9 cloud image"
image_source_uri  = "https://dl.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"

# VM variables
vm_count                = "30"
vm_name_prefix          = "test"
vm_description          = "harold.gutierrez@nutanix.com"
vm_vcpus                = "1"
vm_sockets              = "1"
vm_memory               = "2048"
vm_customization        = "../cloudinit/init.yml"

# Ansible variables
ansible_inventory = "../ansible/inventory"