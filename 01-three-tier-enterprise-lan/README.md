# Three-Tier Enterprise LAN Lab

## Objective

This lab simulates a three-tier enterprise LAN design using Core, Distribution, and Access layers in EVE-NG.

The goal is to practice enterprise switching, VLAN segmentation, high availability, routing, DHCP relay, NAT, ACLs, and basic infrastructure services based on a CCNA/CCNP-style practical exercise.

## Topology

![Topology](topology.png)

## Lab Scenario

The network is divided into multiple sites and VLANs. Each site uses separate VLANs for management, data, servers, and isolated traffic.

The lab focuses on building a scalable enterprise LAN design with redundant gateways, routed uplinks, dynamic routing, and controlled management access.

## Technologies Practiced

* SSH management access
* CDP and LLDP
* VLANs and 802.1Q trunks
* VTP transparent/off mode
* Port Security
* Voice VLAN preparation
* Rapid-PVST
* Layer 3 routed ports
* OSPF Area 0
* Static default route

## Lab Goals

1. Build a three-tier LAN using Core, Distribution, and Access layers.
2. Segment the network using VLANs for management, data, servers, and isolated devices.
3. Configure trunk links between Access and Distribution switches.
4. Configure Rapid-PVST and define STP root priorities.
5. Use routed ports between Distribution and Core layers.
6. Advertise internal networks using OSPF Area 0.
7. Use passive interfaces to prevent unnecessary OSPF hellos toward end-user VLANs.

## VLAN Summary

| VLAN     | Purpose                    |
| -------- | -------------------------- |
| VLAN 10  | Management                 |
| VLAN 20  | Data                       |
| VLAN 30  | Voice                      | 
| VLAN 99  | Trunk Native               |
| VLAN 100 | Servers                    |
| VLAN 999 | Isolated / Native / Unused |

## Routing Design

The lab uses OSPF Area 0 between the Core and Distribution layers. Routed ports are used between Layer 3 devices instead of extending VLAN trunks through the core.

This design keeps Layer 2 boundaries smaller and makes the core routing layer more scalable and stable.

## High Availability

Rapid-PVST is used to control Layer 2 path selection and avoid switching loops.

## Security Features

The lab includes basic enterprise security practices:

* SSH-only remote access
* Local user authentication
* Port Security on access ports
* Native VLAN separation
* Isolated VLAN for unused or restricted ports
* ACL restricting SSH access to management networks only

## Configuration Files

Sanitized device configurations are stored in the `configs` folder.

- [RTR-DC-01 Configuration](configs/RTR-DC-01.txt)
- [RTR-A-01 Configuration](configs/RTR-A-01.txt)
- [RTR-B-01 Configuration](configs/RTR-B-01.txt)
- [CSW-DC-01 Configuration](configs/CSW-DC-01.txt)
- [ASW-DC-01 Configuration](configs/ASW-DC-01.txt)
- [ASW-DC-02 Configuration](configs/ASW-DC-02.txt)
- [CSW-A-01 Configuration](configs/CSW-A-01.txt)
- [ASW-A-01 Configuration](configs/ASW-A-01.txt)
- [CSW-B-01 Configuration](configs/CSW-B-01.txt)
- [ASW-B-01 Configuration](configs/ASW-B-01.txt)

## Verification

Verification commands and test results are documented in [verification.md](verification.md) file.

## Notes

This lab is for learning and documentation purposes. Passwords, hashes, serial numbers, and sensitive values were removed before publishing.
