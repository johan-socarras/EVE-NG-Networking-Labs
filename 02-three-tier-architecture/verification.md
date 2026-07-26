# Network Verification

## Overview

This document provides the commands and validation steps used to verify the three-tier network design.

The verification process covers:

- Interface status
- VLAN and trunk operation
- Spanning Tree
- Layer 3 transit links
- OSPF adjacencies
- Routing tables
- HSRP on the Internet-facing segment
- Inter-VLAN communication
- End-to-end connectivity
- Routed-link failover
- Access-uplink failover
- Core-side HSRP failover

## Verification Summary

| Verification Area | Validation Criteria |
|---|---|
| Physical and logical interfaces | Required interfaces must be operational |
| VLAN configuration | VLANs 10, 20, 30, and 40 must exist on the appropriate switches |
| Trunk links | Access-to-Distribution trunks must carry the assigned VLAN |
| Rapid-PVST | One Access uplink must forward while the alternate remains available |
| Layer 3 transit links | Core and Distribution routed interfaces must be operational |
| OSPF neighbors | Core and Distribution switches must establish the expected adjacencies |
| OSPF routes | Loopback, transit, VLAN, and default routes must be learned correctly |
| HSRP | C-SW-1 should be Active and C-SW-2 Standby for `192.168.116.101` |
| Inter-VLAN routing | Hosts in different VLANs must communicate through the Distribution layer |
| Simulated Internet reachability | Internal hosts must reach the simulated Internet node |
| Routed-link redundancy | Traffic must use an alternate OSPF path after a routed-link failure |
| Access-uplink redundancy | The alternate trunk must forward after the active trunk fails |
| HSRP failover | C-SW-2 must assume the Active role if C-SW-1 becomes unavailable |

---

## 1. Interface Status

### Core and Distribution switches

Run:

```cisco
show ip interface brief
```

Expected result:

- Loopback interfaces are up/up.
- Core-to-Distribution routed interfaces are up/up.
- The Distribution interconnection is up/up.
- The Internet-facing interfaces on both Core switches are up/up.
- Required VLAN interfaces are up/up.

### Access switches

Run:
```cisco
show interfaces status
```

Expected result:

- Both Distribution uplinks are connected.
- The user-facing access port is connected when an end device is active.
- No required interface is administratively disabled.

## 2. VLAN Verification

Run on the Distribution and Access switches:
```cisco
show vlan brief
```

Expected VLAN placement:

| Device |	Required VLANs |
|---|---|
| D-SW-1 | 10, 20, 30, 40 |
| D-SW-2 |	10, 20, 30, 40 |
| A-SW-1 |	10 |
| A-SW-2 |	20 |
| A-SW-3 |	30 |
| A-SW-4 |	40 |

Expected result:
- The VLANs appear as active.
- Each user-facing interface belongs to its assigned VLAN.

## 3. Trunk Verification

### Access-to-Distribution Trunks

Run on each Access switch:

```cisco
show interfaces trunk
```
Expected result:

- Both uplinks operate as 802.1Q trunks.
- Each trunk carries the VLAN assigned to that Access switch.
- One uplink may be forwarding while the other is blocked by Rapid-PVST.
  
| Access Switch |	Allowed VLAN |
|---|---|
| A-SW-1 |	VLAN 10 |
| A-SW-2 |	VLAN 20 |
| A-SW-3 |	VLAN 30 |
| A-SW-4 |	VLAN 40 |
 
### Distribution-to-Distribution Trunk

Run on both Distribution switches:

```cisco
show interfaces trunk
```

Expected result:

- `GigabitEthernet0/3` operates as an 802.1Q trunk.
- VLANs 10, 20, 30, and 40 are allowed and active on the trunk.
- The Layer 2 trunk is separate from the routed OSPF link on `GigabitEthernet0/2`.

Expected VLANs:

| Access Switch |	Allowed VLAN |
|---|---|
| A-SW-1 |	VLAN 10 |
| A-SW-2 |	VLAN 20 |
| A-SW-3 |	VLAN 30 |
| A-SW-4 |	VLAN 40 |

Additional command:
```cisco
show interfaces switchport
```
This command confirms the administrative and operational switchport modes.

## 4. Spanning Tree Verification

Run on the Distribution and Access switches:
```cisco
show spanning-tree root
```

Expected root placement:

| VLAN |	Root Bridge |
|---|---|
| VLAN 10 |	`D-SW-1` |
| VLAN 20 |	`D-SW-2` |
| VLAN 30 |	`D-SW-1` |
| VLAN 40 |	`D-SW-2` |

Run on each Access switch:
```cisco
show spanning-tree vlan 10
show spanning-tree vlan 20
show spanning-tree vlan 30
show spanning-tree vlan 40
```
Use only the command corresponding to the VLAN assigned to that switch.

Expected result:

- One uplink is in the `Forwarding` state.
- The redundant uplink may be in the `Alternate/Blocking` state.
- No Layer 2 loop is present.
- The user-facing port operates as a PortFast edge port.

## 5. Layer 3 Transit Verification

Run on all Core and Distribution switches:
```cisco
show ip interface brief
show interfaces description
```

Expected routed connections:

| Local Device |	Remote Device |	Local Address |
|---|---|---|
| C-SW-1 |	D-SW-1 |	10.0.0.1/30 |
| C-SW-1 |	D-SW-2 |	10.0.0.5/30 |
| C-SW-2 |	D-SW-1 |	10.0.0.9/30 |
| C-SW-2 |	D-SW-2 |	10.0.0.13/30 |
| D-SW-1 |	D-SW-2 |	10.0.0.17/30 |
| D-SW-2 |	D-SW-1 |	10.0.0.18/30 |

Test each directly connected neighbor with `ping`.

Example from C-SW-1:
```cisco
ping 10.0.0.2
ping 10.0.0.6
```
Expected result:
```
Success rate is 100 percent
```

## 6. OSPF Neighbor Verification

Run:
```cisco
show ip ospf neighbor
```
Expected neighbor relationships:

| Device |	Expected OSPF Neighbors |
|---|---|
|C-SW-1 |	D-SW-1 and D-SW-2 |
|C-SW-2 |	D-SW-1 and D-SW-2 |
|D-SW-1 |	C-SW-1, C-SW-2, and D-SW-2 |
|D-SW-2 |	C-SW-1, C-SW-2, and D-SW-1 |

Expected result:

- All required adjacencies reach the FULL state.
- Router IDs match the configured loopback addresses.

Router IDs:

| Device |	Router ID |
|---|---|
| C-SW-1 |	10.222.0.1 |
| C-SW-2 |	10.222.0.2 |
| D-SW-1 |	10.222.0.3 |
| D-SW-2 |	10.222.0.4 |

Additional commands:
```cisco
show ip ospf interface brief
show ip protocols
```

## 7. Routing Table Verification

Run:
```cisco
show ip route
show ip route ospf
```
Expected result:

- Core switches learn the user VLAN networks through OSPF.
- Distribution switches learn remote VLAN and loopback networks.
- Distribution switches receive a default route through OSPF.
- Multiple equal-cost routes may appear when redundant paths are available.

Verify the default route on Distribution:
```cisco
show ip route 0.0.0.0
```
Expected result:

- An OSPF external default route points toward the Core layer.

Verify loopback reachability:
```cisco
ping 10.222.0.1
ping 10.222.0.2
ping 10.222.0.3
ping 10.222.0.4
```

## 8. HSRP Verification

HSRP is implemented only on the Core interfaces facing the simulated Internet segment.

Run on both Core switches:
```cisco
show standby brief
```
Expected result:

| Device |	State |	Physical IP |	Virtual IP |
|---|---|---|---|
| C-SW-1 |	Active |	192.168.116.102 |	192.168.116.101 |
| C-SW-2 |	Standby |	192.168.116.103 |	192.168.116.101 |

C-SW-1 should become Active because it has the higher HSRP priority.

Detailed verification:
```cisco
show standby
```

Confirm:

- HSRP version 2 is active.
- Group 116 uses virtual IP `192.168.116.101`.
- C-SW-1 has priority 110.
- C-SW-2 has priority 100.
- Preemption is enabled.

## 9. Inter-VLAN Connectivity

Example end-device addressing:

| Device |	Address |	Gateway |
|---|---|
| PC-1 |	10.10.10.100/24 |	10.10.10.1 |
| PC-2 |	10.10.20.100/24 |	10.10.20.1 |
| PC-3 |	10.10.30.100/24 |	10.10.30.1 |
| PC-4 |	10.10.40.100/24 |	10.10.40.1 |

Test each local gateway first.

From PC-1:
```cisco
ping 10.10.10.1
```
Then test communication between VLANs:
```cisco
ping 10.10.20.100
ping 10.10.30.100
ping 10.10.40.100
```
Expected result:

- The local default gateway responds.
- Hosts in different VLANs communicate successfully.
- Traffic is routed through the Distribution and Core topology as required.

## 10. Simulated Internet Connectivity

From each Core switch:
```cisco
ping 192.168.116.2
```
Expected result:

- Both Core switches can reach the simulated Internet node.

From the Distribution switches:
```cisco
ping 192.168.116.2
```
From each end device:
```cisco
ping 192.168.116.2
```
Expected result:

- Internal traffic follows the OSPF default route toward the Core layer.
- The simulated Internet node is reachable from all internal VLANs.

## 11. Routed-Link Failover Test

Generate continuous traffic between an internal host and a remote destination.

Example:
```cisco
ping 192.168.116.2
```
Disable one Core-to-Distribution link.

Example:
```cisco
interface GigabitEthernet0/1
 shutdown
```
Verify:
```cisco
show ip ospf neighbor
show ip route
traceroute 192.168.116.2
```
Expected result:

- The OSPF adjacency on the disabled link goes down.
- OSPF recalculates the route.
- Traffic uses an alternate Core-to-Distribution path.
- Connectivity resumes after convergence.

Restore the interface:
```cisco
interface GigabitEthernet0/1
 no shutdown
```
## 12. Access Uplink Failover Test

Generate continuous traffic from an Access-layer host.

Disable the forwarding uplink on the corresponding Access switch:
```cisco
interface GigabitEthernet0/0
 shutdown
```
Verify:
```cisco
show spanning-tree vlan 10
show interfaces trunk
```
Use the VLAN number assigned to the Access switch being tested.

Expected result:

- The alternate uplink transitions to the Forwarding state.
- Host connectivity resumes through the remaining Distribution uplink.
- No switching loop occurs.

Restore the interface:
```cisco
interface GigabitEthernet0/0
 no shutdown
```

## 13. HSRP Failover Test

While continuously pinging the HSRP virtual IP or another reachable address, disable the Internet-facing interface on C-SW-1:
```cisco
interface GigabitEthernet0/0
 shutdown
```
Run on C-SW-2:
```cisco
show standby brief
```
Expected result:

- C-SW-2 transitions from Standby to Active.
- C-SW-2 assumes virtual IP 192.168.116.101.
- The interruption is limited to the HSRP convergence period.

Restore C-SW-1:
```cisco
interface GigabitEthernet0/0
 no shutdown
```
Because preemption is enabled and C-SW-1 has a higher priority, it should regain the Active role.

## 14. Useful Troubleshooting Commands
```cisco
show running-config
show ip interface brief
show interfaces description
show interfaces trunk
show interfaces switchport
show vlan brief
show spanning-tree root
show spanning-tree blockedports
show ip ospf neighbor
show ip ospf interface brief
show ip protocols
show ip route
show ip route ospf
show standby brief
show standby
show cdp neighbors
show cdp neighbors detail
ping
traceroute
```

## Final Verification Result

The verification process confirms:

- Correct VLAN segmentation
- Redundant Access uplinks
- Rapid-PVST operation
- Operational Layer 3 transit links
- Full OSPF adjacencies
- Dynamic route propagation
- Inter-VLAN communication
- Default-route distribution
- HSRP operation on the Internet-facing segment
- Alternate path availability after a link failure

The HSRP placement is intentionally limited to the simulated Internet-facing segment and is not presented as the default gateway mechanism for the internal user VLANs.
