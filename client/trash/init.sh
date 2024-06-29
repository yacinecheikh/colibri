qemu-img create -f qcow2 storage 1G
sudo modprobe nbd
sudo qemu-nbd -c /dev/nbd0 storage
sudo cryptsetup luksFormat /dev/nbd0
sudo cryptsetup open /dev/nbd0 storage
sudo mkfs.btrfs /dev/mapper/storage

sudo cryptsetup close storage
sudo qemu-nbd -d /dev/nbd0
sudo modprobe -r nbd



# sudo modprodbe nbd
# qemu-img create -f qcow2 storage 1G
# sudo qemu-nbd -c /dev/nbd0 storage
# sudo cryptsetup luksFormat /dev/nbd0
# sudo cryptsetup open /dev/nbd0 colibri-data
# sudo mkfs.btrfs /dev/mapper/colibri-data
# unshare -Urm
# sudo unshare -m

"""
"""
