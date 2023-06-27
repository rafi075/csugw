# Windows Machine
## Table of Contents
- [Windows Machine](#windows-machine)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Host Configuration](#host-configuration)
    - [Loopback Adapter Installtion](#loopback-adapter-installtion)
    - [Loopback Adapter Configuration](#loopback-adapter-configuration)
  - [:heavy\_check\_mark: Next Step](#heavy_check_mark-next-step)


## Prerequisites
> Installation pack is included in [Releases](https://github.com/rafi075/csugw/releases/tag/v0.2)
- Windows 10 Pro x64
  - Version: `build 19045.2006 10.0`
- [GNS3](https://gns3.com/software/download)
  - Username:
    ```
    pjackim@colostate.edu
    ```
  - Password:
    ```
    CyberSIM
    ```
  - [GNS3 Virtual Machine](https://gns3.com/software/download-vm), can also be installed by GNS3 installer
- [VMware Workstation 17 Pro](https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html)
  - Version: `17.0.0 build-20800274`


## Host Configuration
Configuration of the Windows Host machine


### Loopback Adapter Installtion
1. ***Disable Windows Firewall***
2. Open CMD
3. Execute `hdwwiz.exe`
<br><img src="https://i.postimg.cc/mrjw8qqx/windows-hdwwiz-0.png" height="100"> <br>


4. Click `Next`
<br><img src="https://i.postimg.cc/SsKG5dFn/windows-hdwwiz-1.png" height="200"> <br>


5. Choose to install hardware manually then click `Next`
<br><img src="https://i.postimg.cc/wvbkdNg0/windows-hdwwiz-2.png" height="300"> <br>


6. Choose `Network adapters`, then click `Next`
<br><img src="https://i.postimg.cc/nrjGVLLZ/windows-hdwwiz-3.png" height="300"> <br>


7. Select `Microsoft` as the manufacturer, and choose the `KM-TEST Loopback Adapter`. Click Next twice to install the adapter and Finish.
<br><img src="https://i.postimg.cc/0jTdzq6S/windows-hdwwiz-4.png" height="300"> <br>


8. Verify that the adapter is installed
>Start > Settings > Control Panel > Network and Sharing Center > Change Adapter Settings
<br><img src="https://i.postimg.cc/KcR63rkc/windows-hdwwiz-5.png" height="200"> <br>


### Loopback Adapter Configuration
1. Navigate to Network Adapters
>Start > Settings > Control Panel > Network and Sharing Center > Change Adapter Settings
2. Right click the loopback adapter
<br><img src="https://i.postimg.cc/KcR63rkc/windows-hdwwiz-5.png" height="200"> <br>


3. Select `Properties`
4. Find `Internet Protocol Version 4 (TCP/IPv4)`
5. Select `Properties`
<br><img src="https://i.postimg.cc/Y92X7kgq/windows-adapter-0.png" height="400"> <br>


6. Check `Use the following IP address`
7. Input an IP address and subnet mask
<br><img src="https://i.postimg.cc/N0kNZLKz/windows-adapter-1.png" height="400"> <br>


8. Click `Ok` to confirm settings

<br>

---

## [:heavy_check_mark: Next Step](./vmplayer.md)
