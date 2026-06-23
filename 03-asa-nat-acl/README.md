# Multi-Site Network Lab with ASA Firewall

## Objective

This lab simulates a small multi-site network using Cisco routers, switches, an ASA firewall, and Linux servers in EVE-NG.

The goal is to practice routing, firewall filtering, NAT, inter-site connectivity, and basic network troubleshooting between Site-A, Site-B, an external client, and an ISP/server network.

## Topology

![Topology](topology.png)

## Network Summary

- Site-A LAN: 192.168.1.0/24
- Site-B LAN: 10.100.100.0/24
- ASA outside network: 203.0.113.0/30
- ASA inside network: 192.0.2.0/30
- Site-A to Site-B transit: 192.0.2.4/30
- Site-B to ISP transit: 192.0.2.8/30
- ISP server network: 4.4.4.0/29

## Devices
--------------------------------------------------------------------
|  Device  | Description                                           |
--------------------------------------------------------------------
| R-Client | External client router                                |
| ASAv     | Firewall between external client and internal network |
| SW-A     | Site-A Layer 3 switch                                 |
| SW-B     | Site-B Layer 3 switch                                 |
| R-ISP    | ISP router                                            |
| PC-A     | Site-A client                                         |
| Server-A | Site-B internal server                                | 
| Server-B | Site-B internal server                                |
| Server   | External server                                       |
--------------------------------------------------------------------

## IP Addressing
--------------------------------------------------------------------
| Device   | Interface | IP Address       | Description            |
--------------------------------------------------------------------
| R-Client | Gi0/0     | 203.0.113.1/30   | Toward ASA outside     |
| ASAv     | Gi0/0     | 203.0.113.2/30   | Outside interface      |
| ASAv     | Gi0/1     | 192.0.2.1/30     | Inside interface       |
| SW-A     | Gi0/3     | 192.0.2.2/30     | Toward ASA             |
| SW-A     | Gi0/2     | 192.0.2.5/30     | Toward SW-B            |
| SW-B     | Gi0/2     | 192.0.2.6/30     | Toward SW-A            |
| SW-B     | Gi0/3     | 192.0.2.9/30     | Toward R-ISP           |
| R-ISP    | Gi0/1     | 192.0.2.10/30    | Toward SW-B            |
| R-ISP    | Gi0/0     | 4.4.4.1/29       | Toward external server |
| PC-A     | eth0      | 192.168.1.11/24  | Site-A client          |
| Server-A | eth0      | 192.168.1.10/24  | Site-A server          |
| Server-A | eth0      | 10.100.100.10/24 | Site-B server          |
| Server-B | eth0      | 10.100.100.11/24 | Site-B server          |
| Server   | eth0      | 4.4.4.4/29       | External server        |
--------------------------------------------------------------------

## Technologies Practiced

- Cisco IOS basic configuration
- Cisco ASA basic configuration
- Static routing or dynamic routing
- Firewall ACLs
- NAT
- Inter-site connectivity
- Network troubleshooting

## Configuration Files

Configuration files are stored in the `configs` folder.

- [R-Client Configuration](configs/R-Client.txt)
- [ASA Configuration](configs/ASA.txt)
- [SW-A Configuration](configs/SW-A.txt)
- [SW-B Configuration](configs/SW-B.txt)
- [R-ISP Configuration](configs/R-ISP.txt)
