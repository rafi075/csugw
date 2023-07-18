# Arch Linux Virtual Node
## Table of Contents
- [Arch Linux Virtual Node](#arch-linux-virtual-node)
  - [Table of Contents](#table-of-contents)
  - [General Information](#general-information)
  - [Tools](#tools)
  - [Pushing Changes](#pushing-changes)

## General Information
- I have found that using two different copies of the Arch Linux node is ideal for testing and updating. One node should be the `Master` node and should have the ability to connect to the internet. The second node should be a clone of the `Master` node, but should not be connected to the internet as it will be used in GNS3. This practice, while slow, mitigates the risk of numerous seemingly random errors and provides peace of mind as the master node is never changed by experiments within GNS3. 
  - `Master` node, connected to the internet: 
  ![img1](https://github.com/rafi075/csugw/assets/78711391/e4033dd9-1b6d-4739-b894-75adf1035947)
  - Clone of `Master` node (***be sure to do a full clone***): 
  ![node2](https://github.com/rafi075/csugw/assets/78711391/b59fc428-ab01-4bc1-ab9c-6f1c7147def0)
  - Notes:
      - It is absolutely essential that the networking devices on the virtual machines are configured as shown above. I have written scripts that configure the machine based on the number of network interfaces it has. Two interfaces indicate the machine should be connected to the internet (thus enabling DHCP), while one interface indicates the machine should be statically configured by the python code, thus networking is disabled.
      - When making changes to the virtual machine, always shutdown the machine via the `shutdown 0` command. This is required for your changes to be *consistently* permanent.
      - After cloning the `Master` node to a `Worker` node or `ArchGNS3`, start the node through VMware. Give it a few seconds to startup, then shut it down. This is not strictly necessary, however, historically it has resolved a very inconsistent where the node was not properly configured when started by GNS3. 



## Tools

## Pushing Changes