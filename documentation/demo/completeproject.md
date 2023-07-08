# GNS3 Complete Project


## Table of Contents

- [GNS3 Complete Project](#gns3-complete-project)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
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
> - `PC`
> - `Switch`
> - `Router`
>   - [Router Installation](../setup/gns3.md)
>
> <br><img src="https://github.com/rafi075/csugw/assets/78711391/5b493189-c5c6-431b-87d4-e5ff606f32d5" alt="proj1" height="500"/><br><br>

> Add a link to the `Cloud (GNS3VM)` using the third network adapter (Bidged `Loopback adapater`).<br>
> Then connect all the devices. The subsequent interfaces do not matter.
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
>   ip add 10.1.1.120 255.255.255.0
>   
>   # Prevent interface shutdown
>   no shut
>   exit
>
>   # Ping Host to confirm connectivity
>   ping 10.1.1.100
>
>   # Write the configuration to prevent having to do this every time
>   write
>```
>
>> These commands will differ depending on the router that you are configuring. These commands are specific to Cisco routers. If you would like to follow exactly as I do, I am using the c3645 router which can be downlaoded from the `Release` page. These images were found through the third party, not Cisco... use it at your own risk.

> Start the `PC (PC1)` and open a console: <br>
> Assign an IP address to the interface using the commands below (default subnet is applied).
<br><img src="https://github.com/rafi075/csugw/assets/78711391/8254484f-80c2-4fe9-adc7-a24d8e8bd503" alt="proj4" height="500"/><br><br>

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

<br><img src="https://github.com/rafi075/csugw/assets/78711391/fd067ab5-940f-4674-8a3c-da0679e7708a" height="400"><br>

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
