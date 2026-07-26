# IP Addressing Plan

## Overview

This document defines the IP addressing used throughout the three-tier network architecture.

The addressing scheme separates:

- User VLAN networks
- Layer 3 transit links
- Loopback interfaces
- The simulated Internet-facing segment

Point-to-point routed links use `/30` networks to conserve address space and clearly identify each connection.

## Loopback Interfaces

Loopback interfaces are used as stable router IDs for OSPF.

| Device | Interface | IP Address |
|---|---|---|
| `C-SW-1` | Loopback0 | `10.222.0.1/32` |
| `C-SW-2` | Loopback0 | `10.222.0.2/32` |
| `D-SW-1` | Loopback0 | `10.222.0.3/32` |
| `D-SW-2` | Loopback0 | `10.222.0.4/32` |

## Core-to-Distribution Transit Links

Each Core switch connects to both Distribution switches through routed Layer 3 interfaces.

| Connection | Transit Network | Device | IP Address |
|---|---|---|---|
| C-SW-1 ↔ D-SW-1 | `10.0.0.0/30` | C-SW-1 | `10.0.0.1/30` |
|  |  | D-SW-1 | `10.0.0.2/30` |
| C-SW-1 ↔ D-SW-2 | `10.0.0.4/30` | C-SW-1 | `10.0.0.5/30` |
|  |  | D-SW-2 | `10.0.0.6/30` |
| C-SW-2 ↔ D-SW-1 | `10.0.0.8/30` | C-SW-2 | `10.0.0.9/30` |
|  |  | D-SW-1 | `10.0.0.10/30` |
| C-SW-2 ↔ D-SW-2 | `10.0.0.12/30` | C-SW-2 | `10.0.0.13/30` |
|  |  | D-SW-2 | `10.0.0.14/30` |

## Distribution Interconnection

A routed Layer 3 link connects the two Distribution switches.

| Connection | Transit Network | Device | IP Address |
|---|---|---|---|
| D-SW-1 ↔ D-SW-2 | `10.0.0.16/30` | D-SW-1 | `10.0.0.17/30` |
|  |  | D-SW-2 | `10.0.0.18/30` |

This link provides an additional OSPF path between the Distribution switches.

## Distribution Layer 2 Trunk

In addition to the routed OSPF link, the Distribution switches use a separate Layer 2 trunk.

| Device | Interface | Remote Device | Allowed VLANs |
|---|---|---|---|
| `D-SW-1` | `GigabitEthernet0/3` | `D-SW-2` | 10, 20, 30, 40 |
| `D-SW-2` | `GigabitEthernet0/3` | `D-SW-1` | 10, 20, 30, 40 |

The routed and switched connections use separate physical interfaces.

The trunk carries the user VLANs between the Distribution switches and supports Access-uplink redundancy without extending OSPF over the Layer 2 connection.

## User VLAN Networks

The user networks are divided into four VLANs.

| VLAN | Name | Subnet | Default Gateway | Primary Distribution Switch |
|---|---|---|---|---|
| 10 | USERS-10 | `10.10.10.0/24` | `10.10.10.1` | `D-SW-1` |
| 20 | USERS-20 | `10.10.20.0/24` | `10.10.20.1` | `D-SW-2` |
| 30 | USERS-30 | `10.10.30.0/24` | `10.10.30.1` | `D-SW-1` |
| 40 | USERS-40 | `10.10.40.0/24` | `10.10.40.1` | `D-SW-2` |

The VLAN gateway interfaces are distributed across both Distribution switches to balance Layer 3 responsibilities.

HSRP is not used for the internal VLAN gateways in this lab.

## Access Switch Management

Each Access switch uses an IP address from the VLAN it serves.

| Device | Management VLAN | Management IP | Default Gateway |
|---|---|---|---|
| `A-SW-1` | VLAN 10 | `10.10.10.10/24` | `10.10.10.1` |
| `A-SW-2` | VLAN 20 | `10.10.20.10/24` | `10.10.20.1` |
| `A-SW-3` | VLAN 30 | `10.10.30.10/24` | `10.10.30.1` |
| `A-SW-4` | VLAN 40 | `10.10.40.10/24` | `10.10.40.1` |

## Example End Devices

| Device | VLAN | IP Address | Default Gateway |
|---|---|---|---|
| PC-1 | VLAN 10 | `10.10.10.100/24` | `10.10.10.1` |
| PC-2 | VLAN 20 | `10.10.20.100/24` | `10.10.20.1` |
| PC-3 | VLAN 30 | `10.10.30.100/24` | `10.10.30.1` |
| PC-4 | VLAN 40 | `10.10.40.100/24` | `10.10.40.1` |

## Simulated Internet-Facing Segment

Both Core switches connect to the same network as the simulated Internet node.

| Device or Function | IP Address |
|---|---|
| `C-SW-1` physical address | `192.168.116.102/24` |
| `C-SW-2` physical address | `192.168.116.103/24` |
| HSRP virtual IP | `192.168.116.101/24` |
| Simulated Internet node | `192.168.116.2/24` |

## HSRP Placement

HSRP is intentionally configured on the Core interfaces facing the simulated Internet node.

The virtual IP is:

```text
192.168.116.101
```
This provides a shared redundant Core-side address on the external lab segment.

This differs from the more common campus implementation in which HSRP provides the default gateway for internal user VLANs.

The placement was selected specifically for the requirements of this simulated topology.

## OSPF Addressing

OSPF process 1 advertises:

- `10.222.0.0/24` loopback address range
- `10.0.0.0/24` transit-link address range
- `10.10.10.0/24`
- `10.10.20.0/24`
- `10.10.30.0/24`
- `10.10.40.0/24`

The loopback addresses are used as manually configured OSPF router IDs.

## Default Routing

Both Core switches use a default route toward the simulated Internet node:

```cisco
ip route 0.0.0.0 0.0.0.0 192.168.116.2
```
### Return Route from the Simulated Internet Node

The simulated Internet node uses the HSRP virtual IP as the next hop for traffic returning toward the internal networks.

```text
Destination: 10.0.0.0/8
Next hop: 192.168.116.101
```

The default route is advertised into OSPF so that the Distribution layer can reach the simulated Internet segment.

## Addressing Summary

| Address Range | Purpose |
|---|---|
| `10.222.0.0/24` | Loopback interfaces |
| `10.0.0.0/24` | Layer 3 transit links |
| `10.10.10.0/24` | VLAN 10 |
| `10.10.20.0/24` | VLAN 20 |
| `10.10.30.0/24` | VLAN 30 |
| `10.10.40.0/24` | VLAN 40 |
| `192.168.116.0/24` | Simulated Internet-facing segment |
