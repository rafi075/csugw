# GNS3 First Project
>
> GNS3 can run on the host machine, but it is recommended to leverage the GNS3 VM for enhanced virtualization ability. This guide will use the GNS3 VM.

## Table of Contents

- [GNS3 First Project](#gns3-first-project)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
  - [Result](#result)
  - [Testing](#testing)

## Setup

1. Create a new project and wait for both servers to be running
<br><img src="https://i.postimg.cc/yY2rZMqv/firstproj-proj-0.png" height="100"><br>

>Initialize the following devices:
>
> - `Cloud`
> - `PC`
> - `Switch`
> - `Router`
>   - [Router Installation](../setup/gns3.md)
>
> <br><img src="https://i.postimg.cc/q7bQ9mbZ/proj1.gif" alt="proj1" height="500"/><br><br>

> Add a link to the `Cloud (GNS3VM)` using the third network adapter (Bidged `Loopback adapater`).<br>
> Then connect all the devices. The subsequent interfaces do not matter.
>
><br><img src="https://i.postimg.cc/RhfRJvMj/proj2.gif" alt="proj2" height="500"/><br><br>

> Start the `Router (R1)` and open a console.<br>
> Enter the commands below to configure the router's interface
><br><img src="https://i.postimg.cc/QdjbVLvy/proj3.gif" alt="proj3" height="500"/><br><br>
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
>   ip add 10.1.1.120 255.255.255.0
>   
>   # Prevent interface shutdown
>   no shut
>   exit
>
>   # Ping Host to confirm connectivity
>   ping 10.1.1.100
>```
>
>> These commands will differ depending on the router that you are configuring. These commands are specific to Cisco routers. If you would like to follow exactly as I do, I am using the c3645 router which can be downlaoded from the `Release` page. These images were found through the third party, not Cisco... use it at your own risk.

> Start the `PC (PC1)` and open a console: <br>
> Assign an IP address to the interface using the commands below (default subnet is applied).
<br><img src="https://i.postimg.cc/xTDgDN5Y/proj4.gif" alt="proj4" height="500"/><br><br>

```bash
   # Show IP summary
   show ip 
   
   # Configure 
   ip 10.1.1.130
   
   # Confirm configuration in IP summary
   show ip 

   # Ping Host to confirm connectivity
   ping 10.1.1.100
```

---

## Result

<br><img src="https://i.postimg.cc/wBnRyPwN/2023-05-20-18-37.png" height="400"><br>

The configurations yeild the following:
| Host                  | IP Address  | Mask           | Interface  |
|---------------------- |------------ |--------------- |----------- |
| Windows Host (Cloud)  | 10.1.1.100  | 255.255.255.0  | eth2       |
| Router (R1)           | 10.1.1.120  | 255.255.255.0  | f0/0       |
| VirtualPC (PC1)       | 10.1.1.130  | 255.255.255.0  | e0         |

---

## Testing

To confirm everything is working, you should be able to ping any device from any other device, including the host machine. Ensure your results match the ping matrix below.

| Ping-able             | :heavy_check_mark: Windows Host (Cloud)       | :heavy_check_mark: Router (R1)                | :heavy_check_mark: VirtualPC (PC1)            |
|---------------------- |--------------------------- |--------------------------- |--------------------------- |
| :heavy_check_mark: Windows Host (Cloud)  | 10.1.1.100 --> 10.1.1.100  | 10.1.1.100 --> 10.1.1.120  | 10.1.1.100 --> 10.1.1.130  |
| :heavy_check_mark: Router (R1)           | 10.1.1.120 --> 10.1.1.100  | 10.1.1.120 --> 10.1.1.120  | 10.1.1.120 --> 10.1.1.130  |
| :heavy_check_mark: VirtualPC (PC1)       | 10.1.1.130 --> 10.1.1.100  | 10.1.1.130 --> 10.1.1.120  | 10.1.1.130 --> 10.1.1.130  |
