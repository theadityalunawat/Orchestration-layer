# Orchestration-layer

Cloud Technologies used are:

1) Libvirt : libvirt is an open source API, daemon and management tool for managing platform virtualization. It can be used to manage KVM, Xen, VMware ESX, QEMU and other virtualization technologies. These APIs are widely used in the orchestration layer of hypervisors in the development of a cloud-based solution

 2). Qemu : QEMU is a generic and open source machine emulator and virtualizer. When used as a machine emulator, QEMU can run OSes and programs made for one machine (e.g. an ARM board) on a different machine (e.g. your own PC). By using dynamic translation, it achieves very good performance.

3) KVM : If your hardware supports virtualisation, we use KVM else we use Xen.
KVM (Kernel-based Virtual Machine) is a virtualization infrastructure for the Linux kernel that turns it into a hypervisor. It was merged into the Linux kernel mainline in kernel version 2.6.20, which was released on February 5, 2007. KVM requires a processor with hardware virtualization extension.


Hypervisor : It is actually VM manager, that manages all the resources of hardware.

To download all these tools together, use the following link:
http://www.howtogeek.com/117635/how-to-install-kvm-and-create-virtual-machines-on-ubuntu/


or directly run the following commands :

sudo apt-get install qemu-kvm libvirt-bin bridge-utils virt-manager

If you find any error in this, contact me.

After installing all these things, we will need an ISO file, of any OS.(I have Ubuntu 14.04 ISO downloaded with me).

Now restart the system.

Now on unity search bar :- search for virtual machine manager, open it and create a VM following the above link, because we need an image file(which contains the whole OS from its hard disk to everything say it as C drive of windows compiles as a file).


Now using this image file you can create as many VMS as you want of type ubuntu 14.04 for your users. You can start them, stop them, destroy them and create them.

Now follow the link to create connection to hypervisor and perform the following functions :
https://joepettit.com/python-libvirt/
Or if you dont understand, just copy paste the below code in a python file:

To connect to hypervisor write this code in a python file:

import libvirt

def connect():  
    connection = libvirt.open("qemu:///system")
# This code is used to connect to the qemu system, in order to perform all the operations.

To perform the functions, use the following code below this connection.
	 
-To list all the existing VM's on your system :

x=connection.listDefinedDomains()
print x
# Here x is a variable

-To start,stop and delete a VM:
#First search it by name and then start it.
# Say my VM name is “aditya”
vm = connection.lookupByName("aditya")
vm.create()
#This will start the vm aditya. Here vm is also a variable

vm.destroy()
# this will stop the VM.
vm.undefine()

# This will delete the VM.

Now most importantly how to create VM using python script.

1) Configuration of an existing VM is stored in an XML file.
Dump that file.

Say for ex. My VM name is aditya , so the command will be:
sudo virsh dumpxml aditya > vm.xml
# We are redirecting the output to vm. Xml.

Now open this file and find and change the following parameters:
1) <boot dev='hd'/> to <boot dev='cdrom'/>
2) Remove the whole tag that contains path of .iso file.
3) Give a new name to VM <name>newname</name>
4)Give new uuid to VM <uuid>48 bit id, change any one character only(Dont change no. By alphabet or vice versa)</uuid>
Now run the following pyhton script and keep this xml file in the same folder.

xml = ""  
with open(path_to_xml_config, "r") as file:  
    xml = file.read()
connection.defineXML(xml) 

.
After all this run the following command to check the VM's running or stopped:
virsh list --all 
 



