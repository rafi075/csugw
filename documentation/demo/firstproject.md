# GNS3 First Project
> GNS3 can run on the host machine, but it is recommended to leverage the GNS3 VM for enhanced virtualization ability. This guide will use the GNS3 VM.

## Table of Contents
- [GNS3 First Project](#gns3-first-project)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
  - [Testing](#testing)


## Setup
1. Create a new project and wait for both servers to be running
<br><img src="https://i.postimg.cc/yY2rZMqv/firstproj-proj-0.png" height="100"> alt="firstproj-proj-0"/><br>



2. Initialize the following devices:
   - `Cloud`
   - `Router`
      - [Router Installation](../setup/gns3.md)
   - `PC`

<br><img src="https://i.postimg.cc/brs3GT37/firstproj-proj-1.png" height="300"> alt="firstproj-proj-1"/><br>



3. Add a link to the `Cloud` using the third network adapter. Then connect all the devices. The subsequent interfaces do not matter.
<br><img src="https://i.postimg.cc/j2mvy71L/firstproj-proj-2.png" height="200"> alt="firstproj-proj-2"/><br>


4. Start the router and open a console
<br><img src="https://i.postimg.cc/zGW2Sx85/firstproj-proj-3.png" height="100"> alt="firstproj-proj-3"/><br>


5. Enter the following commands in order:

    ```bash
    # Show IP interface brief
    show ip int br
    
    # Configure 
    conf t
    
    # Select an interface
    # fa0/0 = FastEthernet0/0 (as shown by show ip int br)
    int fa0/0
    
    # Manually configure the IP address for the selected interface
    ip add 10.1.1.101 255.255.255.0
    
    # Prevent interface shutdown
    no shut
    ```

> These commands will differ depending on the router that you are configuring. These commands are specific to Cisco routers. If you would like to follow exactly as I do, I am using the c3600 router which can be found in the GNS3 setup section. These images were found through the third party, not Cisco... use it at your own risk.

5.1 - `show ip int br` Output:
<br><img src="https://i.postimg.cc/Px6Srczb/firstproj-router-0.png" height="200"> alt="firstproj-router-0"/><br>


After the commands have been executed, `FastEthernet0/0` will be assigned an IP address of `10.1.1.101`, which can be confirmed by running `show ip int br` again.
 

## Testing
At this point you should be able to ping the router's interface from the host machine
<br><img src="https://i.postimg.cc/2jK0ss5r/firstproj-test-0.png" height="300"> alt="firstproj-test-0"/><br>

