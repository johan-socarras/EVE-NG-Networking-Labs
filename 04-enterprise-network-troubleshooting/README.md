# Multi-Site Enterprise Network Troubleshooting Lab

A realistic multi-site enterprise network designed for advanced Cisco networking practice and troubleshooting.

This lab simulates a corporate environment with three geographically separated sites, redundant Layer 2 and Layer 3 infrastructure, multiple VLANs, dynamic and static routing, first-hop redundancy, network security, DHCP, DNS, NAT/PAT, and several intentionally introduced network faults.

The objective is not simply to configure the network, but to **investigate realistic user incidents, identify root causes, and restore connectivity without redesigning the network**.

---

## Lab Overview

**Difficulty:** Advanced  
**Environment:** EVE-NG  
**Topology:** Three-site enterprise network  
**Primary Vendors:** Cisco IOS / Cisco vIOS  
**Automation:** Python + EVE-NG REST API

### Network Sites

- Headquarters (HQ)
- Branch Office
- Disaster Recovery (DR)

Each site contains:

- 2 Layer 3 distribution switches
- 2 Layer 2 access switches
- 3 VLANs
- Multiple VPC endpoints
- Redundant uplinks
- First-hop redundancy
- Layer 2 redundancy

The three sites are interconnected through a routed WAN.

---

## Topology

```text
                              ┌───────────────┐
                              │     R1-HQ     │
                              │   WAN Router  │
                              └───────┬───────┘
                                      │
                         ┌────────────┼────────────┐
                         │                         │
                       R2-BR                       R3-DR
                    Branch Router              DR Router
                         │                         │
             ┌───────────┴───────────┐   ┌────────┴─────────┐
             │                       │   │                  │
        BR-DIST-A               BR-DIST-B              DR-DIST-A
             │                       │                     │
        ┌────┴────┐             ┌────┴────┐          ┌────┴────┐
        │         │             │         │          │         │
     BR-ACC-1  BR-ACC-2      Access    Access      DR-ACC-1  DR-ACC-2
        │         │
       PCs       PCs


                     HEADQUARTERS

                       R1-HQ
                         │
              ┌──────────┴──────────┐
              │                     │
          HQ-DIST-A             HQ-DIST-B
              │                     │
        ┌─────┴─────┐         ┌─────┴─────┐
        │           │         │           │
     HQ-ACC-1    HQ-ACC-2   Access      Access
        │           │
       PCs         PCs
```

The final topology contains approximately:

| Device Type | Quantity |
|---|---:|
| WAN Routers | 3 |
| Layer 3 Distribution Switches | 6 |
| Layer 2 Access Switches | 6 |
| VPC Endpoints | 9 |
| **Total** | **24** |

---

# Technologies Covered

This laboratory intentionally combines multiple Cisco networking technologies.

## Layer 2

- VLANs
- 802.1Q trunking
- STP
- RSTP
- Root bridge election
- DTP
- VTP
- EtherChannel
- Port Security
- Access ports
- Trunk ports
- VLAN troubleshooting

## Layer 3

- Inter-VLAN routing
- Subnetting
- Static routing
- OSPF
- Route selection
- Routing redundancy
- HSRP

## Network Services

- DHCP
- DNS
- NAT
- PAT

## Security

- Standard ACLs
- Extended ACLs
- Port Security
- VLAN segmentation
- Management VLAN

---

# VLAN Architecture

Each site contains three functional VLANs.

## Headquarters

| VLAN | Name | Subnet |
|---:|---|---|
| 10 | USERS | 10.10.10.0/24 |
| 20 | SERVERS | 10.10.20.0/24 |
| 30 | VOICE | 10.10.30.0/24 |

HSRP virtual gateways:

```text
VLAN 10 → 10.10.10.1
VLAN 20 → 10.10.20.1
VLAN 30 → 10.10.30.1
```

---

## Branch Office

| VLAN | Name | Subnet |
|---:|---|---|
| 110 | USERS | 10.20.10.0/24 |
| 120 | SERVERS | 10.20.20.0/24 |
| 130 | GUEST | 10.20.30.0/24 |

HSRP virtual gateways:

```text
VLAN 110 → 10.20.10.1
VLAN 120 → 10.20.20.1
VLAN 130 → 10.20.30.1
```

---

## Disaster Recovery

| VLAN | Name | Subnet |
|---:|---|---|
| 210 | USERS | 10.30.10.0/24 |
| 220 | SERVERS | 10.30.20.0/24 |
| 230 | MANAGEMENT | 10.30.30.0/24 |

HSRP virtual gateways:

```text
VLAN 210 → 10.30.10.1
VLAN 220 → 10.30.20.1
VLAN 230 → 10.30.30.1
```

---

# WAN Addressing

The routers form a routed triangle.

```text
R1-HQ ↔ R2-BRANCH
172.16.12.0/30

R2-BRANCH ↔ R3-DR
172.16.23.0/30

R3-DR ↔ R1-HQ
172.16.31.0/30
```

This design provides multiple routing paths between sites.

OSPF will be used as the primary dynamic routing protocol.

Static routes will also be configured for selected destinations and backup paths.

---

# Layer 2 Design

Each site uses redundant access-to-distribution connectivity.

```text
                 DIST-A
                /      \
               /        \
          EtherChannel   \
             /            \
          ACC-1 ---------- ACC-2
               \          /
                \        /
                 DIST-B
```

STP/RSTP provides loop prevention.

EtherChannel provides link redundancy and increased logical bandwidth.

The lab intentionally creates situations where STP, EtherChannel, trunking, and VLAN configuration must be investigated.

---

# HSRP

The two Layer 3 distribution switches at each site provide redundant default gateways.

Example:

```text
                HSRP
                 │
        ┌────────┴────────┐
        │                 │
    DIST-A             DIST-B
   Active               Standby
        │                 │
        └──── Virtual ────┘
             Gateway
```

The HSRP virtual IP is used as the default gateway for clients.

Troubleshooting may involve:

- HSRP priority
- Active/standby state
- Interface status
- VLAN availability
- Routing
- Incorrect gateway configuration

---

# OSPF

OSPF provides dynamic routing between the three sites.

Expected topology:

```text
                R1
              /    \
             /      \
           R2────────R3
```

The routed triangle provides multiple paths.

Possible troubleshooting scenarios include:

- Incorrect OSPF area
- Missing network statement
- Passive interface
- Incorrect subnet
- Neighbor adjacency failure
- Missing route
- Incorrect routing decision

---

# DHCP

Clients obtain their addressing dynamically.

Example:

```text
VLAN 10
10.10.10.0/24

DHCP:
Network       10.10.10.0/24
Default GW    10.10.10.1
DNS Server    10.10.20.53
```

Possible failures:

- Incorrect DHCP pool
- Incorrect default gateway
- Incorrect DNS server
- Missing DHCP relay
- Incorrect VLAN
- Exhausted address range

---

# DNS

The environment contains an internal DNS service.

Users should be able to resolve internal resources by hostname.

Example:

```text
server01.corp.local
dns01.corp.local
```

A realistic incident may therefore appear as:

> "The server is online, but users report that the application is down."

The actual problem may be DNS rather than the application itself.

---

# NAT / PAT

The HQ router provides simulated Internet access.

PAT allows multiple internal clients to share the external address.

Example:

```text
Internal Network
      │
      ▼
   R1-HQ
      │
     PAT
      │
      ▼
  External Network
```

Troubleshooting scenarios may involve:

- Incorrect NAT inside/outside
- Incorrect ACL
- Missing NAT statement
- Incorrect interface
- PAT configuration
- Routing toward the external network

---

# ACL

Access-control policies are used to restrict traffic between VLANs and sites.

Examples:

```text
USERS → SERVERS
Allowed

GUEST → INTERNAL SERVERS
Denied

MANAGEMENT → NETWORK DEVICES
Allowed
```

A deliberately incorrect ACL may cause an apparently unrelated application failure.

---

# Port Security

Access ports use port-security controls.

Possible configuration includes:

- Maximum MAC addresses
- Sticky MAC addresses
- Violation actions

A user may report:

> "My workstation suddenly lost network connectivity."

The actual cause could be a port-security violation.

---

# VTP

VTP is used to demonstrate centralized VLAN management.

The environment contains VTP relationships between appropriate switches.

Troubleshooting scenarios may include:

- Incorrect VTP domain
- Incorrect VTP mode
- VLAN missing from a switch
- Trunk failure
- VLAN database inconsistency

---

# DTP

Dynamic Trunking Protocol is included to demonstrate automatic trunk negotiation.

The lab may contain intentionally incorrect combinations of:

```text
switchport mode
switchport trunk
DTP negotiation
```

This can create situations where a link that should be a trunk is operating as an access link.

---

# Troubleshooting Scenarios

The lab is designed around realistic IT incidents rather than isolated configuration exercises.

The user will receive an incident report rather than being told which protocol is broken.

Example:

## Incident INC-1047

> **John cannot access Server-01**
>
> John from the Headquarters Users department reports that he cannot access Server-01.
>
> His workstation receives an IP address successfully, but the application hosted on Server-01 is unreachable.
>
> Other users are reporting intermittent connectivity problems.
>
> The network team performed maintenance on the distribution switches earlier today.
>
> No configuration changes were officially documented.
>
> Investigate the network and identify the root causes.
>
> Restore normal connectivity without redesigning the network.

---

# Potential Fault Categories

The lab can contain multiple simultaneous faults.

Examples include:

### Layer 2

- Incorrect VLAN assignment
- Missing VLAN
- Incorrect trunk
- DTP mismatch
- VTP inconsistency
- EtherChannel member mismatch
- STP root bridge issue
- RSTP configuration issue
- Port-security violation

### Layer 3

- Incorrect IP address
- Incorrect subnet mask
- Incorrect default gateway
- HSRP failure
- Missing route
- Incorrect static route
- OSPF neighbor failure
- Incorrect OSPF area
- Missing OSPF network statement

### Services

- DHCP pool error
- DHCP relay issue
- Incorrect DNS address
- DNS reachability problem

### Security

- Incorrect ACL
- Guest traffic incorrectly permitted
- Server traffic incorrectly blocked
- Management traffic blocked

### NAT

- Incorrect NAT interface
- Incorrect overload configuration
- Missing NAT rule
- Incorrect routing toward the external network

---

# Troubleshooting Philosophy

The goal is to troubleshoot the network as an engineer would in a real production environment.

The user should not immediately know:

- Which device is broken
- Which protocol is broken
- How many problems exist
- Whether the problems are related
- Whether there are multiple root causes

The expected workflow is:

```text
User Complaint
      ↓
Define the Scope
      ↓
Check Layer 1/2
      ↓
Check VLANs / Trunks
      ↓
Check STP / EtherChannel
      ↓
Check HSRP
      ↓
Check Routing
      ↓
Check OSPF / Static Routes
      ↓
Check ACL
      ↓
Check DHCP / DNS
      ↓
Check NAT/PAT
      ↓
Identify Root Cause
      ↓
Fix Configuration
      ↓
Verify End-to-End Connectivity
```

---

# Lab Automation

The laboratory is being built using Python and the EVE-NG REST API.

The long-term architecture is:

```text
                 ┌──────────────┐
                 │     User     │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │     LLM      │
                 └──────┬───────┘
                        │
                 Lab Specification
                        │
                        ▼
              ┌────────────────────┐
              │  Python Lab Manager │
              └─────────┬──────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │    EVE-NG    │
                 └──────────────┘
```

The automation will eventually be able to:

- Generate a topology
- Create an EVE-NG lab
- Create nodes
- Create networks
- Create links
- Configure devices
- Start devices
- Verify topology
- Verify connectivity
- Inject faults
- Store the expected solution

---

# Hidden Solution

Each troubleshooting scenario will have an internal solution.

Example:

```json
{
  "incident": "INC-1047",
  "faults": [
    {
      "device": "HQ-ACC-1",
      "problem": "VLAN 20 is missing",
      "solution": "Create VLAN 20"
    },
    {
      "device": "HQ-DIST-B",
      "problem": "Incorrect HSRP priority",
      "solution": "Restore the intended HSRP priority"
    },
    {
      "device": "R1-HQ",
      "problem": "Incorrect NAT configuration",
      "solution": "Correct the NAT overload configuration"
    }
  ]
}
```

The solution is intentionally hidden from the student.

---

# Learning Objectives

After completing this laboratory, the student should be able to troubleshoot:

- VLAN segmentation
- Trunking
- DTP
- VTP
- STP/RSTP
- EtherChannel
- HSRP
- Inter-VLAN routing
- OSPF
- Static routing
- DHCP
- DNS
- ACLs
- NAT/PAT
- Port Security
- Subnetting
- Multi-site enterprise connectivity

More importantly, the student should learn how these technologies interact.

---

# Verification

A successful solution should restore:

- Inter-VLAN connectivity
- Inter-site connectivity
- Server accessibility
- DNS resolution
- DHCP operation
- Internet/PAT connectivity
- HSRP redundancy
- OSPF adjacency
- Expected Layer 2 topology
- Security policies

The objective is not merely to make one ping work.

The entire network should return to its intended operational state.

---

# Project Structure

```text
INC-1047-Multi-Site-Enterprise/
│
├── README.md
│
├── topology/
│   └── topology.yml
│
├── automation/
│   ├── build_lab.py
│   ├── eve_api.py
│   ├── topology.py
│   └── verify.py
│
├── configs/
│   ├── routers/
│   ├── distribution/
│   └── access/
│
├── scenarios/
│   └── INC-1047.md
│
└── solution/
    └── solution.md
```

---

# Status

This laboratory is currently under development.

### Completed

- [x] EVE-NG API authentication
- [x] Automated lab creation
- [x] Automated vIOS node creation
- [x] vIOS template verification

### In Progress

- [ ] Multi-site topology
- [ ] Network creation
- [ ] Automated links
- [ ] Device startup
- [ ] Topology verification
- [ ] Base configurations

### Planned

- [ ] VLAN configuration
- [ ] STP/RSTP
- [ ] VTP
- [ ] DTP
- [ ] EtherChannel
- [ ] HSRP
- [ ] DHCP
- [ ] DNS
- [ ] OSPF
- [ ] Static routing
- [ ] ACL
- [ ] NAT/PAT
- [ ] Port Security
- [ ] Fault injection
- [ ] Automated scenario generation
- [ ] Hidden solution generation
- [ ] AI-generated troubleshooting labs

---

# Disclaimer

This laboratory is intended for educational and networking practice purposes.

All failures are intentionally introduced for troubleshooting exercises.

No production network should be modified based on this laboratory without appropriate testing and validation.
