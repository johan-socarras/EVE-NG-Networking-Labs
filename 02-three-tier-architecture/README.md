# Three-Tier Redundant Architecture Lab

## Objective

This lab documents a three-tier enterprise network built in EVE-NG using Core, Distribution, and Access layers.

The design focuses on:

- Layer 3 redundancy between Core and Distribution switches
- Redundant uplinks between network layers
- HSRP gateway redundancy
- VLAN segmentation
- Dynamic routing
- Enterprise network availability

## Documentation Notice

The original lab was completed and tested in EVE-NG.

The original virtual lab environment and device configuration files were later lost during a system migration. The documentation and configuration files in this folder are being reconstructed from the original topology, addressing notes, and design information.

Reconstructed configuration files are not presented as original `show running-config` outputs. They represent a technically consistent recreation of the original design.

## Topology

![Topology Diagram](topology.png)

## Network Design

### Core Layer

The Core layer contains two Layer 3 switches:

- `C-SW-1`
- `C-SW-2`

Each Core switch connects to both Distribution switches using routed Layer 3 links.

The Core switches also provide redundant connectivity toward the simulated Internet edge.

### Distribution Layer

The Distribution layer contains:

- `D-SW-1`
- `D-SW-2`

Each Distribution switch connects to both Core switches.

The Distribution switches also have a direct connection between them to provide additional redundancy and routing continuity.

### Access Layer

The Access layer contains four switches:

- `A-SW-1`
- `A-SW-2`
- `A-SW-3`
- `A-SW-4`

Each Access switch is dual-homed to both Distribution switches.

Each Access switch provides connectivity for one user VLAN and subnet.

## Device Roles and Loopback Addresses

| Device | Layer | Loopback 0 | Role |
|---|---|---:|---|
| `C-SW-1` | Core | `10.222.0.1/32` | Primary Core switch |
| `C-SW-2` | Core | `10.222.0.2/32` | Secondary Core switch |
| `D-SW-1` | Distribution | `10.222.0.3/32` | Primary Distribution switch |
| `D-SW-2` | Distribution | `10.222.0.4/32` | Secondary Distribution switch |
| `A-SW-1` | Access | N/A | Access switch for VLAN 10 |
| `A-SW-2` | Access | N/A | Access switch for VLAN 20 |
| `A-SW-3` | Access | N/A | Access switch for VLAN 30 |
| `A-SW-4` | Access | N/A | Access switch for VLAN 40 |

## VLAN and Subnet Summary

| VLAN | Subnet | Access Switch |
|---|---|---|
| VLAN 10 | `10.10.10.0/24` | `A-SW-1` |
| VLAN 20 | `10.10.20.0/24` | `A-SW-2` |
| VLAN 30 | `10.10.30.0/24` | `A-SW-3` |
| VLAN 40 | `10.10.40.0/24` | `A-SW-4` |

## Internet Edge Redundancy

The Core switches use HSRP on the network facing the simulated Internet edge.

| Device | Interface Address |
|---|---|
| `C-SW-1` | `192.168.116.102` |
| `C-SW-2` | `192.168.116.103` |
| HSRP Virtual IP | `192.168.116.101` |
| Internet Gateway | `192.168.116.2` |

The HSRP virtual address provides a consistent Layer 3 gateway for the network.

If the active Core switch becomes unavailable, the standby Core switch can assume the virtual gateway role.

## Routing Design

The network uses routed Layer 3 links between the Core and Distribution switches.

This reduces the Layer 2 failure domain and provides multiple routing paths between the Core and Distribution layers.

OSPF is used to advertise:

- Core loopback networks
- Distribution loopback networks
- Routed transit links
- User VLAN networks
- The default route toward the Internet edge

## Redundancy Design

The lab includes multiple forms of redundancy:

- Two Core switches
- Two Distribution switches
- Full-mesh Layer 3 links between Core and Distribution
- Direct routing link between Distribution switches
- Dual-homed Access switches
- HSRP gateway redundancy
- Dynamic routing through OSPF

The objective is to maintain network connectivity when an individual link or network device becomes unavailable.

## Technologies Practiced

- Three-tier enterprise architecture
- Layer 3 switching
- Routed switch ports
- VLAN segmentation
- 802.1Q trunking
- HSRP
- OSPF
- Loopback interfaces
- Redundant uplinks
- Default route propagation
- Network troubleshooting
- Cisco IOS verification commands

## Lab Goals

1. Build a three-tier network using Core, Distribution, and Access layers.
2. Configure routed links between the Core and Distribution switches.
3. Establish OSPF neighbor relationships across the Layer 3 links.
4. Advertise loopbacks, transit links, and VLAN subnets through OSPF.
5. Configure redundant uplinks for Access switches.
6. Configure HSRP toward the simulated Internet edge.
7. Verify that internal VLANs can communicate across the network.
8. Verify that network connectivity continues after a link or device failure.
9. Document the reconstructed configurations and validation process.

## Reconstructed Configuration Files

Reconstructed device configurations will be stored in the `configs` folder.

Planned files:

- `configs/C-SW-1.txt`
- `configs/C-SW-2.txt`
- `configs/D-SW-1.txt`
- `configs/D-SW-2.txt`
- `configs/A-SW-1.txt`
- `configs/A-SW-2.txt`
- `configs/A-SW-3.txt`
- `configs/A-SW-4.txt`

These files are reconstructed from the original design and should be reviewed and tested before being considered fully validated.

## Verification

A separate `verification.md` file will include:

- VLAN and trunk verification
- Routed-interface verification
- OSPF neighbor verification
- Routing-table verification
- HSRP verification
- End-to-end connectivity tests
- Redundancy and failover tests

Because the original lab environment was lost, new command outputs should only be added after the reconstructed topology is recreated and tested.

## Current Status

| Component | Status |
|---|---|
| Original topology | Completed |
| Original lab implementation | Completed |
| Original testing | Completed |
| Original device configurations | Lost during system migration |
| README reconstruction | Completed |
| Configuration reconstruction | In progress |
| New verification outputs | Pending lab recreation |

## Notes

This project is intended for learning, technical documentation, and portfolio purposes.

Passwords, hashes, serial numbers, and sensitive values must be removed or changed before publishing any reconstructed configuration files.
