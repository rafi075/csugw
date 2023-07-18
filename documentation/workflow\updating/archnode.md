# Arch Linux Virtual Node
> Please note, sections marked with ":exclamation:" are things I consider important to know.

## Table of Contents
- [Arch Linux Virtual Node](#arch-linux-virtual-node)
  - [Table of Contents](#table-of-contents)
  - [General Information](#general-information)
  - [Pushing Changes](#pushing-changes)
    - [Pushing Changes - Bug Collection](#pushing-changes---bug-collection)
  - [Tools](#tools)

## General Information
- I have found that using two different copies of the Arch Linux node is ideal for testing and updating. One node should be the `Master` node and should have the ability to connect to the internet. The second node should be a clone of the `Master` node, but should not be connected to the internet as it will be used in GNS3. This practice, while slow, mitigates the risk of numerous seemingly random errors and provides peace of mind as the master node is never changed by experiments within GNS3. 
  - `Master` node, connected to the internet: 

  ![img1](https://github.com/rafi075/csugw/assets/78711391/e4033dd9-1b6d-4739-b894-75adf1035947)
  - Clone of `Master` node (***be sure to do a full clone***): 
  
  ![node2](https://github.com/rafi075/csugw/assets/78711391/b59fc428-ab01-4bc1-ab9c-6f1c7147def0)
  - Notes:
      - :exclamation: It is absolutely essential that the networking devices on the virtual machines are configured as shown above. I have written scripts that configure the machine based on the number of network interfaces it has. Two interfaces indicate the machine should be connected to the internet (thus enabling DHCP), while one interface indicates the machine should be statically configured by the python code, thus networking is disabled.

      - :exclamation: When making changes to the virtual machine, always shutdown the machine via the `shutdown 0` command. This is required for your changes to be *consistently* permanent.

      - After cloning the `Master` node to a `Worker` node or `ArchGNS3`, start the node through VMware. Give it a few seconds to startup, then shut it down. This is not strictly necessary, however, historically it has resolved a very inconsistent where the node was not properly configured when started by GNS3. 


## Pushing Changes
- I encourage you to use GitHub to manage your changes to this project as well as to distribute code changes to the master node. In my opinion, resolving the VM internet connection issue will be easier than trying to transfer changes to the master node via USB (issues will likely arise with VMware and Arch Linux). Any mention of changes to this project will assumed to be done through GitHub.
- Change management in this project is a burden as changes must be distributed to nodes which may or may not be connected to the internet. Below, I will outline the steps I followed to push changes.
  1. Make changes to the code base on a local branch
  2. Add changes, Commit changes, and push the branch to GitHub
    ```bash
    git add -A
    git commit -m "Description of changes"
    git push -u origin branch_name
    ```
  3. Open the `Master` node described in [General Information](#general-information)
     1. The `Master` node may continuiously loop on startup. If this is the case, simply press `ctrl + c` to exit the loop.
  4. Currently, we have made changes to the `branch_name` branch, however by default, the `Master` node is using the `master` branch. Therefore, we need to update the repository and switch branches:
    ```bash
    git fetch
    git pull
    git checkout branch_name
    ```
  5. Now the `Master` node is using the `branch_name` branch, and has your latest changes.
  6. "Save" your changes by running `shutdown 0` to shutdown the VM.
  7. Once the shutdown is complete, clone the `Master` node to create a `Worker` node or `ArchGNS3` node (the name does not matter). Reference [General Information](#general-information) to see how to configure the network devices on these machines.
  8. Now, open the `Worker` node VM through VMWare. This is a dry run of the node to ensure that the network settings are configured before GNS3 clones the node. Again, this should not be necessary, but it solves a rare issue. Once you see the image below, `ctrl + c` to kill the program and `shutdown 0` to exit the node.

  ![nodeconf](https://github.com/rafi075/csugw/assets/78711391/3dbcbf85-12f6-4420-8ba1-091ff606c9b6)

  9. Now the `Worker` node is fully configured and loaded with your changes. It is ready to be imported into GNS3 and used in a project.

### Pushing Changes - Bug Collection
> I am by no means an expert on why these happen. I will provide my experience and my assumptions to hopefully help you.
- When importing a new or updated VM into GNS3, an issue can arise where GNS3 seemingly does not use the VM provided by the import process. It seems this is because the new VM uses the same name as a previously imported (then deleted) VM, therefore GNS3 is matching the name with the previous VM. Key takeaway, be cautious of using the same name as a previously imported VM. It is unclear if this is caused by GNS3, VMWare API, or something else. I have not tested whether restarting GNS3 solve this issue.
- Shutting down an Arch Linux node via the `Shudown` button in VMWare results in some changes not being saved to the disk. To resolve this, always use the `shutdown 0` command instead. This could potentially be the problem if experiment results from GNS3 are not saved to disk of the nodes -- untested.
- Modifying the `Worker` node to have an internet connection, syncing changes, then reconfiguring the `Worker` node to remove the internet connection can work and save you the need to reimport the VM into GNS3. However, an issue eventually arises where the GNS3 node no longer is up to date with the node in VMWare. I have no idea why this is. If you can make this work, it is a slightly faster method as you do not need to fully clone the master VM and you do not need to reimport the VM into GNS3 for testing.
- Not a bug, but a potential user error: be sure you know which branch your changes are on, and which branch your nodes are currently using.

## Tools

