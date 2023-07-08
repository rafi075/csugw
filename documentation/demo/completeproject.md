# GNS3 Complete Project


## Table of Contents

- [GNS3 Complete Project](#gns3-complete-project)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
    - [Second Node](#second-node)
  - [Result](#result)
  - [Testing](#testing)

## Setup

1. Clone the repository on the Windows host machine
2. Follow the steps outlined in [windows setup](../setup/windows.md) and [VMware setup](../setup/vmplayer.md). **To follow this doc, use `GATEWAY_IP = 10.1.1.1` and `GATEWAY_NETMASK = 255.255.0.0`**

 Create a new project and wait for both servers to be running
<br><img src="https://github.com/rafi075/csugw/assets/78711391/7cbf67b6-bce2-4d35-8e90-81f888797764" height="100"><br>

>Initialize the following devices:
>
> - `Cloud`
> - `Switch`
> - `Router`
>   - [Router Installation](../setup/gns3.md)
>
>> Do not worry about the `PC1` shown in the visual below
>
> <br><img src="https://github.com/rafi075/csugw/assets/78711391/5b493189-c5c6-431b-87d4-e5ff606f32d5" alt="proj1" height="500"/><br><br>

> Add a link to the `Cloud (GNS3VM)` using the third network adapter (Bidged `Loopback adapater`).<br>
> Then connect all the devices. The subsequent interfaces do not matter.
>
>> Do not worry about the `PC1` shown in the visual below
>
><br><img src="https://github.com/rafi075/csugw/assets/78711391/f116872b-4474-47b9-b60d-c31fc24fdbf5" alt="proj2" height="500"/><br><br>

> Start the `Router (R1)` and open a console.<br>
> Enter the commands below to configure the router's interface
><br><img src="https://github.com/rafi075/csugw/assets/78711391/e8f3acab-ca7f-4435-99a9-2bc777484d97" alt="proj3" height="500"/><br><br>
>
>```bash
>   # Show IP interface brief
>   show ip int br
>   
>   # Configure 
>   conf t
>   
>   # Select an interface
>   # fa0/0 = FastEthernet0/0 (as shown by `show ip int br`)
>   int fa0/0
>  
>   # Manually configure the IP address for the selected interface
>   ip add 10.1.2.1 255.255.255.0
>   
>   # Prevent interface shutdown
>   no shut
>   exit
>
>   # Ping Host to confirm connectivity
>   ping 10.1.1.1
>
>   # Write the configuration to prevent having to do this every time
>   write
>```
>
>> These commands will differ depending on the router that you are configuring. These commands are specific to Cisco routers. If you would like to follow exactly as I do, I am using the c3645 router which can be downlaoded from the `Release` page. These images were found through the third party, not Cisco... use it at your own risk.
>
> I highly encourage you to export the configuration, allowing the router to automatically import the configuration when the project starts. Below is an animation to show you how:
><br><img src="https://github.com/rafi075/csugw/assets/78711391/4091bfe5-898a-4cd7-849b-769d5a943d2c" alt="proj3" height="400"/><br><br>




 - Start the server on the Windows machine
 - [After importing the Arch node](../setup/gns3.md), add it to the project and connect it. 
 - Start the Arch node through GNS3. This initialization process requires a bit of patience. The node will go through an automatic restart
 - Once the node has completed initialization, the server CLI should display the currently connected clients, as shown below the animation.
<br><img src="https://github.com/rafi075/csugw/assets/78711391/db821932-f4fc-444c-bfea-17980766c600" alt="proj4" height="500"/><br><br>

- Successful node initialization
<br><img src="https://github.com/rafi075/csugw/assets/78711391/20905538-280d-4a67-b882-10be21cdba56" height="145"><br>


- Next I will confirm that the node has successfully been initialized and connected to the server. 
- I ping the linux node from the host machine, and validate that the node information is consistent with the configuration file.
<br><img src="https://github.com/rafi075/csugw/assets/78711391/458af708-9e4e-4291-a09e-d6bc7d2cb353" height="500"><br>


---

### Second Node

Identical steps as above.

<br><img src="https://github.com/rafi075/csugw/assets/78711391/fbdf27bf-d996-4ee6-8880-68ed495f0483" height="500"><br>


---

## Result





<br><img src="https://github.com/rafi075/csugw/assets/78711391/ce0fcd92-859a-4d36-8796-1153a18fed7e" height="400"><br>

The configurations yeild the following:
| Host                  | IP Address  | Mask           | Interface  |
|---------------------- |------------ |--------------- |----------- |
| Windows Host (Cloud)  | 10.1.1.1  | 255.255.0.0  | eth2       |
| Router (R1)           | 10.1.2.1  | 255.255.0.0  | f0/0       |
| Arch Node (Arch-1)       | 10.1.1.160  | 255.255.255.0  | ens33         |
| Arch Node (Arch-2)       | 10.1.1.170  | 255.255.255.0  | ens33         |

---

## Testing

To confirm everything is working, you should be able to ping any device from any other device, including the host machine. Ensure your results match the ping matrix below.

| Ping-able             | :heavy_check_mark: Windows Host (Cloud)       | :heavy_check_mark: Router (R1)                | :heavy_check_mark: Arch-1             | :heavy_check_mark: Arch-2             |
|---------------------- |--------------------------- |--------------------------- |--------------------------- |--------------------------- |
| :heavy_check_mark: Windows Host (Cloud)  | 10.1.1.1 --> 10.1.1.1  | 10.1.1.1 --> 10.1.2.1  | 10.1.1.1 --> 10.1.1.160  |10.1.1.1 --> 10.1.1.170  |
| :heavy_check_mark: Router (R1)           | 10.1.2.1 --> 10.1.1.1  | 10.1.2.1 --> 10.1.2.1  | 10.1.2.1 --> 10.1.1.160  |10.1.2.1 --> 10.1.1.170  |
| :heavy_check_mark: Arch-1        | 10.1.1.160 --> 10.1.1.1  | 10.1.1.160 --> 10.1.2.1  | 10.1.1.160 --> 10.1.1.160  |10.1.1.160 --> 10.1.1.170  |
| :heavy_check_mark: Arch-2        | 10.1.1.170 --> 10.1.1.1  | 10.1.1.170 --> 10.1.2.1  | 10.1.1.170 --> 10.1.1.160  |10.1.1.170 --> 10.1.1.170  |
