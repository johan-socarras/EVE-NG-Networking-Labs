# EVE-NG Networking Labs

This repository contains hands-on networking labs built and documented in EVE-NG, focused on Cisco routing, switching, firewalling, redundancy, network security, and troubleshooting.

The purpose of this repository is to demonstrate practical networking skills through topology diagrams, configuration files, verification commands, test results, and troubleshooting documentation.

## Featured Labs

### 1. Multi-Site Collapsed-Core Enterprise Network

A three-site enterprise LAN: access switches, a multilayer switch per site doing
both distribution and core, and site routers meshed in a WAN triangle. Inter-site
routing is static, summarised per site, and tied to IP SLA probes so a failed
link is actually withdrawn.

Technologies practiced:

- VLAN segmentation and 802.1Q trunking
- Rapid-PVST with deterministic root placement
- EtherChannel between access and multilayer
- OSPF area 0 within each site, authenticated, with pinned router IDs
- Summarised static routing with IP SLA, object tracking and floating backups
- DHCP relay, with the pools on the site routers
- Bidirectional ACL filtering on an isolated VLAN
- Port security, DHCP snooping and Dynamic ARP Inspection
- SSH-only management with a VTY access-class
- NTP hierarchy

[View Lab](multi-site-collapsed-core/README.md)

### 2. Three-Tier Redundant Architecture

A three-tier network focused on Layer 3 redundancy, redundant uplinks, HSRP, and VLAN segmentation.

The original lab was completed in EVE-NG. Some documentation and configuration files are being reconstructed after the original lab environment was lost during a system migration.

[View Lab](02-three-tier-architecture/README.md)

### 3. Cisco ASA Destination NAT and ACL Lab

A firewall lab demonstrating how external clients can access an internal server through a fixed destination IP using Cisco ASA destination NAT and ACLs.

Technologies practiced:

- Cisco ASA
- Destination NAT
- Access control lists
- Static and dynamic routing
- Inter-site connectivity
- Firewall troubleshooting
- Connectivity verification

[View Lab](03-asa-nat-acl/README.md)

## Skills Demonstrated

- Cisco IOS and ASA configuration
- Enterprise routing and switching
- VLANs and Layer 2 segmentation
- Dynamic and static routing
- First-hop redundancy
- Route summarisation and floating static routes
- Path liveness detection with IP SLA and object tracking
- Layer 2 hardening: port security, DHCP snooping, DAI
- Firewall traffic control
- NAT and ACL implementation
- Network troubleshooting and verification
- Technical documentation using GitHub

## Documentation Format

Each completed lab may include:

- Topology diagram
- Business or technical scenario
- Network objectives
- IP addressing and device roles
- Sanitized configuration files
- Verification commands
- Test results
- Troubleshooting notes
- Final conclusions

## Security and Privacy

Passwords, hashes, serial numbers, public credentials, and sensitive values are removed or changed before publishing.

All public IP addresses and network scenarios are used only inside isolated lab environments unless otherwise stated.

## About

These labs were created to strengthen practical networking skills and document hands-on experience with Cisco routing, switching, firewalling, redundancy, and troubleshooting.
