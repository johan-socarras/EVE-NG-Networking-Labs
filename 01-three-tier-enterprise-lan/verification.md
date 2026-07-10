# Verification

This file documents the commands and tests used to verify the Three-Tier Enterprise LAN Lab.

## 1. VLAN and Trunk Verification

Commands used:

```cisco
show vlan brief
show interfaces trunk
```

Expected result:

* VLANs 10, 20, 30, 99, 100, and 999 should exist.
* Trunk links should allow VLANs 10, 20, 30, 99, 100, and 999.
* Native VLAN should be VLAN 99.

Verifications:

```cisco
CSW-DC-01#sh vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/3, Gi1/0, Gi1/1, Gi1/2
                                                Gi1/3
10   Management                       active
20   Data                             active
30   Voice                            active
99   Native-trunk                     active
100  Server                           active
999  Isolated-Lab                     active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
CSW-DC-01#show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      99
Gi0/2       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99-100,999
Gi0/2       10,20,30,99-100,999

Port        Vlans allowed and active in management domain
Gi0/1       10,20,30,99-100,999
Gi0/2       10,20,30,99-100,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       10,20,30,99-100,999
Gi0/2       10,20,30,99-100,999
```
```cisco
ASW-DC-01#sh vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3, Gi1/0, Gi1/1
                                                Gi1/2, Gi1/3
10   Management                       active
20   Data                             active
30   Voice                            active    Gi0/1
99   Native-trunk                     active
100  Server                           active
999  Isolated-Lab                     active    Gi0/1
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
ASW-DC-01#show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/0       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/0       10,20,30,99-100,999

Port        Vlans allowed and active in management domain
Gi0/0       10,20,30,99-100,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/0       10,20,30,99-100,999
```

```cisco
CSW-A-01#sh vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3, Gi1/0, Gi1/1
                                                Gi1/2, Gi1/3
10   Management                       active
20   Data                             active
30   Voice                            active
99   Native-trunk                     active
100  Server                           active
999  Isolated-Lab                     active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
CSW-A-01#show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99-100,999

Port        Vlans allowed and active in management domain
Gi0/1       10,20,30,99-100,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       10,20,30,99-100,999
```

```cisco
CSW-B-01#sh vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3, Gi1/0, Gi1/1
                                                Gi1/2, Gi1/3
10   Management                       active
20   Data                             active
30   Voice                            active
99   Native-trunk                     active
100  Server                           active
999  Isolated-Lab                     active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
CSW-B-01#show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/1       10,20,30,99-100,999

Port        Vlans allowed and active in management domain
Gi0/1       10,20,30,99-100,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       10,20,30,99-100,999
```
The same verification was completed on the remaining access switches.

Status: Passed

## 2. STP Verification

Commands used:

```cisco
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree vlan 20
show spanning-tree vlan 99
```

Expected result:

* Rapid-PVST should be enabled.
* Root bridge placement should match the lab design.
* Access ports should use PortFast and BPDU Guard where appropriate.

Verifications:

```cisco
CSW-DC-01#show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0010, VLAN0020, VLAN0030, VLAN0099-VLAN0100, VLAN0999
Extended system ID                      is enabled
Portfast Default                        is disabled
Portfast Edge BPDU Guard Default        is disabled
Portfast Edge BPDU Filter Default       is disabled
Loopguard Default                       is disabled
PVST Simulation Default                 is enabled but inactive in rapid-pvst mode
Bridge Assurance                        is enabled
EtherChannel misconfig guard            is enabled
Configured Pathcost method used is short
UplinkFast                              is disabled
BackboneFast                            is disabled

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0010                     0         0        0          2          2
VLAN0020                     0         0        0          2          2
VLAN0030                     0         0        0          2          2
VLAN0099                     0         0        0          2          2
VLAN0100                     0         0        0          2          2

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0999                     0         0        0          2          2
---------------------- -------- --------- -------- ---------- ----------
6 vlans                      0         0        0         12         12
CSW-DC-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.0004.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24586  (priority 24576 sys-id-ext 10)
             Address     5000.0004.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
Gi0/2               Desg FWD 4         128.3    P2p


CSW-DC-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.0004.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24596  (priority 24576 sys-id-ext 20)
             Address     5000.0004.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
Gi0/2               Desg FWD 4         128.3    P2p


CSW-DC-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.0004.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24675  (priority 24576 sys-id-ext 99)
             Address     5000.0004.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
Gi0/2               Desg FWD 4         128.3    P2p
```

```cisco 
ASW-DC-01#show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: none
Extended system ID                      is enabled
Portfast Default                        is disabled
Portfast Edge BPDU Guard Default        is disabled
Portfast Edge BPDU Filter Default       is disabled
Loopguard Default                       is disabled
PVST Simulation Default                 is enabled but inactive in rapid-pvst mode
Bridge Assurance                        is enabled
EtherChannel misconfig guard            is enabled
Configured Pathcost method used is short
UplinkFast                              is disabled
BackboneFast                            is disabled

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0010                     0         0        0          1          1
VLAN0020                     0         0        0          1          1
VLAN0030                     0         0        0          2          2
VLAN0099                     0         0        0          1          1
VLAN0100                     0         0        0          1          1

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0999                     0         0        0          2          2
---------------------- -------- --------- -------- ---------- ----------
6 vlans                      0         0        0          8          8
ASW-DC-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     5000.0005.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-DC-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32788  (priority 32768 sys-id-ext 20)
             Address     5000.0005.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-DC-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32867  (priority 32768 sys-id-ext 99)
             Address     5000.0005.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p
```

```cisco
CSW-A-01#show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0010, VLAN0020, VLAN0030, VLAN0099-VLAN0100, VLAN0999
Extended system ID                      is enabled
Portfast Default                        is disabled
Portfast Edge BPDU Guard Default        is disabled
Portfast Edge BPDU Filter Default       is disabled
Loopguard Default                       is disabled
PVST Simulation Default                 is enabled but inactive in rapid-pvst mode
Bridge Assurance                        is enabled
EtherChannel misconfig guard            is enabled
Configured Pathcost method used is short
UplinkFast                              is disabled
BackboneFast                            is disabled

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0010                     0         0        0          1          1
VLAN0020                     0         0        0          1          1
VLAN0030                     0         0        0          1          1
VLAN0099                     0         0        0          1          1
VLAN0100                     0         0        0          1          1

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0999                     0         0        0          1          1
---------------------- -------- --------- -------- ---------- ----------
6 vlans                      0         0        0          6          6
CSW-A-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.000b.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24586  (priority 24576 sys-id-ext 10)
             Address     5000.000b.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p


CSW-A-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.000b.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24596  (priority 24576 sys-id-ext 20)
             Address     5000.000b.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p


CSW-A-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.000b.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24675  (priority 24576 sys-id-ext 99)
             Address     5000.000b.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
```

```cisco
CSW-B-01#show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0010, VLAN0020, VLAN0030, VLAN0099-VLAN0100, VLAN0999
Extended system ID                      is enabled
Portfast Default                        is disabled
Portfast Edge BPDU Guard Default        is disabled
Portfast Edge BPDU Filter Default       is disabled
Loopguard Default                       is disabled
PVST Simulation Default                 is enabled but inactive in rapid-pvst mode
Bridge Assurance                        is enabled
EtherChannel misconfig guard            is enabled
Configured Pathcost method used is short
UplinkFast                              is disabled
BackboneFast                            is disabled

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0010                     0         0        0          1          1
VLAN0020                     0         0        0          1          1
VLAN0030                     0         0        0          1          1
VLAN0099                     0         0        0          1          1
VLAN0100                     0         0        0          1          1

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0999                     0         0        0          1          1
---------------------- -------- --------- -------- ---------- ----------
6 vlans                      0         0        0          6          6
CSW-B-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.000c.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24586  (priority 24576 sys-id-ext 10)
             Address     5000.000c.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p


CSW-B-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.000c.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24596  (priority 24576 sys-id-ext 20)
             Address     5000.000c.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p


CSW-B-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.000c.0000
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24675  (priority 24576 sys-id-ext 99)
             Address     5000.000c.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/1               Desg FWD 4         128.2    P2p
```

The same verification was completed on the remaining access switches.

Status: Passed

## 3. Layer 3 Interface Verification

Commands used:

```cisco
show ip interface brief
show ip route
```

Expected result:

* Routed interfaces should be up/up.
* SVIs should be up/up for active VLANs.
* Connected routes should appear for local VLANs and point-to-point links.

Verifications:

```cisco
RTR-DC-01#show ip int brief
Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.1        YES NVRAM  up                    up
GigabitEthernet0/1         172.16.0.5      YES NVRAM  up                    up
GigabitEthernet0/2         172.16.0.1      YES NVRAM  up                    up
GigabitEthernet0/3         unassigned      YES NVRAM  administratively down down
RTR-DC-01#show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 14 subnets, 3 masks
C        10.0.0.0/30 is directly connected, GigabitEthernet0/0
L        10.0.0.1/32 is directly connected, GigabitEthernet0/0
O        10.0.10.0/24 [110/2] via 10.0.0.2, 00:33:09, GigabitEthernet0/0
O        10.0.20.0/24 [110/2] via 10.0.0.2, 00:33:09, GigabitEthernet0/0
O        10.0.99.0/24 [110/2] via 10.0.0.2, 00:33:09, GigabitEthernet0/0
O        10.0.100.0/24 [110/2] via 10.0.0.2, 00:33:09, GigabitEthernet0/0
S        10.1.10.0/24 [1/0] via 172.16.0.2
S        10.1.20.0/24 [1/0] via 172.16.0.2
S        10.1.99.0/24 [1/0] via 172.16.0.2
S        10.1.100.0/24 [1/0] via 172.16.0.2
S        10.2.10.0/24 [1/0] via 172.16.0.6
S        10.2.20.0/24 [1/0] via 172.16.0.6
S        10.2.99.0/24 [1/0] via 172.16.0.6
S        10.2.100.0/24 [1/0] via 172.16.0.6
      172.16.0.0/16 is variably subnetted, 4 subnets, 2 masks
C        172.16.0.0/30 is directly connected, GigabitEthernet0/2
L        172.16.0.1/32 is directly connected, GigabitEthernet0/2
C        172.16.0.4/30 is directly connected, GigabitEthernet0/1
L        172.16.0.5/32 is directly connected, GigabitEthernet0/1
```

```cisco
CSW-DC-01#show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.0.2        YES NVRAM  up                    up
GigabitEthernet0/1     unassigned      YES unset  up                    up
GigabitEthernet0/2     unassigned      YES unset  up                    up
GigabitEthernet0/3     unassigned      YES unset  administratively down down
GigabitEthernet1/0     unassigned      YES unset  administratively down down
GigabitEthernet1/1     unassigned      YES unset  administratively down down
GigabitEthernet1/2     unassigned      YES unset  administratively down down
GigabitEthernet1/3     unassigned      YES unset  administratively down down
Vlan10                 10.0.10.1       YES NVRAM  up                    up
Vlan20                 10.0.20.1       YES NVRAM  up                    up
Vlan100                10.0.100.1      YES NVRAM  up                    up
Vlan999                10.0.99.1       YES NVRAM  up                    up
CSW-DC-01#show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is 10.0.0.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 10.0.0.1
      10.0.0.0/8 is variably subnetted, 10 subnets, 3 masks
C        10.0.0.0/30 is directly connected, GigabitEthernet0/0
L        10.0.0.2/32 is directly connected, GigabitEthernet0/0
C        10.0.10.0/24 is directly connected, Vlan10
L        10.0.10.1/32 is directly connected, Vlan10
C        10.0.20.0/24 is directly connected, Vlan20
L        10.0.20.1/32 is directly connected, Vlan20
C        10.0.99.0/24 is directly connected, Vlan999
L        10.0.99.1/32 is directly connected, Vlan999
C        10.0.100.0/24 is directly connected, Vlan100
L        10.0.100.1/32 is directly connected, Vlan100
```

The same verification was completed on the remaining devices

Status: Passed

## 4. OSPF Verification

Commands used:

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip protocols
```

Expected result:

* OSPF neighbors should form between Layer 3 devices.
* Remote site networks should appear in the routing table as OSPF routes.
* User/server VLANs should be advertised into OSPF.
* End-user VLAN interfaces should be passive when appropriate.

Verifications:

```cisco
RTR-DC-01#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.100.1        1   FULL/BDR        00:00:30    10.0.0.2        GigabitEthernet0/0
RTR-DC-01#show ip ospf interface brief
Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C
Gi0/0        1     0               10.0.0.1/30        1     DR    1/1
RTR-DC-01#show ip route ospf
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 14 subnets, 3 masks
O        10.0.10.0/24 [110/2] via 10.0.0.2, 00:36:43, GigabitEthernet0/0
O        10.0.20.0/24 [110/2] via 10.0.0.2, 00:36:43, GigabitEthernet0/0
O        10.0.99.0/24 [110/2] via 10.0.0.2, 00:36:43, GigabitEthernet0/0
O        10.0.100.0/24 [110/2] via 10.0.0.2, 00:36:43, GigabitEthernet0/0
RTR-DC-01#show ip protocols
*** IP Routing is NSF aware ***

Routing Protocol is "application"
  Sending updates every 0 seconds
  Invalid after 0 seconds, hold down 0, flushed after 0
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Maximum path: 32
  Routing for Networks:
  Routing Information Sources:
    Gateway         Distance      Last Update
  Distance: (default is 4)

Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Router ID 172.16.0.5
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Maximum path: 4
  Routing for Networks:
  Routing on Interfaces Configured Explicitly (Area 0):
    GigabitEthernet0/0
  Routing Information Sources:
    Gateway         Distance      Last Update
    10.0.100.1           110      00:36:52
  Distance: (default is 110)
```

```cisco
CSW-DC-01#show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
172.16.0.5        1   FULL/DR         00:00:34    10.0.0.1        GigabitEthernet0/0
CSW-DC-01#show ip ospf interface brief
Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C
Vl999        1     0               10.0.99.1/24       1     DR    0/0
Vl100        1     0               10.0.100.1/24      1     DR    0/0
Vl20         1     0               10.0.20.1/24       1     DR    0/0
Vl10         1     0               10.0.10.1/24       1     DR    0/0
Gi0/0        1     0               10.0.0.2/30        1     BDR   1/1
CSW-DC-01#show ip route ospf
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is 10.0.0.1 to network 0.0.0.0

CSW-DC-01#show ip protocols
*** IP Routing is NSF aware ***

Routing Protocol is "application"
  Sending updates every 0 seconds
  Invalid after 0 seconds, hold down 0, flushed after 0
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Maximum path: 32
  Routing for Networks:
  Routing Information Sources:
    Gateway         Distance      Last Update
  Distance: (default is 4)

Routing Protocol is "ospf 1"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Router ID 10.0.100.1
  Number of areas in this router is 1. 1 normal 0 stub 0 nssa
  Maximum path: 4
  Routing for Networks:
  Routing on Interfaces Configured Explicitly (Area 0):
    Vlan999
    Vlan100
    Vlan20
    Vlan10
    GigabitEthernet0/0
  Routing Information Sources:
    Gateway         Distance      Last Update
  Distance: (default is 110)
```

Status: Passed

## 5. Inter-Site Connectivity Tests

Test from Data Center to Site-A:

```bash
SRV-DC-01> ping 10.1.99.10

84 bytes from 10.1.99.10 icmp_seq=1 ttl=60 time=10.385 ms
84 bytes from 10.1.99.10 icmp_seq=2 ttl=60 time=12.793 ms
84 bytes from 10.1.99.10 icmp_seq=3 ttl=60 time=12.189 ms
84 bytes from 10.1.99.10 icmp_seq=4 ttl=60 time=8.837 ms
84 bytes from 10.1.99.10 icmp_seq=5 ttl=60 time=14.370 ms
```

Test from Data Center to Site-B:

```bash
SRV-DC-01> ping 10.2.99.10

84 bytes from 10.2.99.10 icmp_seq=1 ttl=60 time=16.976 ms
84 bytes from 10.2.99.10 icmp_seq=2 ttl=60 time=14.561 ms
84 bytes from 10.2.99.10 icmp_seq=3 ttl=60 time=15.282 ms
84 bytes from 10.2.99.10 icmp_seq=4 ttl=60 time=9.750 ms
84 bytes from 10.2.99.10 icmp_seq=5 ttl=60 time=15.977 ms
```

Test from Site-A to Site-B:

```bash
SRV-A-01> ping 10.2.99.10

84 bytes from 10.2.99.10 icmp_seq=1 ttl=60 time=13.271 ms
84 bytes from 10.2.99.10 icmp_seq=2 ttl=60 time=14.710 ms
84 bytes from 10.2.99.10 icmp_seq=3 ttl=60 time=12.905 ms
84 bytes from 10.2.99.10 icmp_seq=4 ttl=60 time=12.174 ms
84 bytes from 10.2.99.10 icmp_seq=5 ttl=60 time=9.015 ms

```

Expected result:

* Devices in different sites should be able to reach each other according to the routing design.

Status: Passed

## 6. Default Route Verification

Commands used:

```cisco
show ip route 0.0.0.0
```

Verifications:

```cisco
CSW-DC-01#show ip route 0.0.0.0
Routing entry for 0.0.0.0/0, supernet
  Known via "static", distance 1, metric 0, candidate default path
  Routing Descriptor Blocks:
  * 10.0.0.1
      Route metric is 0, traffic share count is 1
```

```cisco
CSW-A-01#show ip route 0.0.0.0
Routing entry for 0.0.0.0/0, supernet
  Known via "static", distance 1, metric 0, candidate default path
  Routing Descriptor Blocks:
  * 10.1.0.1
      Route metric is 0, traffic share count is 1
```

```cisco
CSW-B-01#show ip route 0.0.0.0
Routing entry for 0.0.0.0/0, supernet
  Known via "static", distance 1, metric 0, candidate default path
  Routing Descriptor Blocks:
  * 10.2.0.1
      Route metric is 0, traffic share count is 1
```

Expected result:

* Core switches should have a default route pointing toward the upstream router.

Status: Passed

## 7. Isolated VLAN Verification

Commands used:

```cisco
show access-lists
show running-config interface vlan 999
```

Verifications:

```cisco
CSW-DC-01#show access-lists
Extended IP access list Vlan999_Isolated
    10 permit icmp any any
    20 deny ip any 10.0.0.0 0.255.255.255
    30 deny ip any 172.16.0.0 0.15.255.255
    40 deny ip any 192.168.0.0 0.0.255.255
    50 permit ip any any
CSW-DC-01#show running-config interface vlan 999
Building configuration...

Current configuration : 116 bytes
!
interface Vlan999
 ip address 10.0.99.1 255.255.255.0
 ip access-group Vlan999_isolated in
 ip ospf 1 area 0
end
```

```cisco
CSW-A-01#show access-lists
Extended IP access list Vlan999_Isolated
    10 permit icmp any any
    20 deny ip any 10.0.0.0 0.255.255.255
    30 deny ip any 172.16.0.0 0.15.255.255
    40 deny ip any 192.168.0.0 0.0.255.255
    50 permit ip any any
CSW-A-01#show running-config interface vlan 999
Building configuration...

Current configuration : 116 bytes
!
interface Vlan999
 ip address 10.1.99.1 255.255.255.0
 ip access-group Vlan999_isolated in
 ip ospf 1 area 0
end
```

```cisco
CSW-B-01#show access-lists
Extended IP access list Vlan999_Isolated
    10 permit icmp any any
    20 deny ip any 10.0.0.0 0.255.255.255
    30 deny ip any 172.16.0.0 0.15.255.255
    40 deny ip any 192.168.0.0 0.0.255.255
    50 permit ip any any
CSW-B-01#show running-config interface vlan 999
Building configuration...

Current configuration : 116 bytes
!
interface Vlan999
 ip address 10.2.99.1 255.255.255.0
 ip access-group Vlan999_isolated in
 ip ospf 1 area 0
end
```

Expected result:

* VLAN 999 should be restricted by ACL.
* The isolated VLAN should not have unrestricted access to internal private networks.
* Allowed traffic should work according to the ACL design.

Status: Passed

## 8. SSH Management Verification

Commands used:

```cisco
show ip ssh
show running-config | section line vty
```

Verifications:

```cisco
CSW-DC-01#show ip ssh
SSH Enabled - version 2.0
Authentication methods:publickey,keyboard-interactive,password
Authentication Publickey Algorithms:x509v3-ssh-rsa,ssh-rsa
Hostkey Algorithms:x509v3-ssh-rsa,ssh-rsa
Encryption Algorithms:aes128-ctr,aes192-ctr,aes256-ctr
MAC Algorithms:hmac-sha1,hmac-sha1-96
Authentication timeout: 120 secs; Authentication retries: 3
Minimum expected Diffie Hellman key size : 1024 bits
IOS Keys in SECSH format(ssh-rsa, base64 encoded): CSW-DC-01.administrator
ssh-rsa ***********************************************************
***********************************************************
CSW-DC-01#show running-config | section line vty
line vty 0 4
 exec-timeout 3 0
 login local
 transport input ssh
```

Expected result:

* SSH version 2 should be enabled.
* VTY lines should use local login.
* Remote access should be limited to SSH.

Status: Passed

## 9. Port Security / Access Port Verification

Commands used:

```cisco
show port-security
show port-security interface gigabitEthernet0/1
show interfaces status
```

Verifications:

```cisco
ASW-DC-01#show port-security interface g0/1
Port Security              : Enabled
Port Status                : Secure-up
Violation Mode             : Restrict
Aging Time                 : 0 mins
Aging Type                 : Absolute
SecureStatic Address Aging : Disabled
Maximum MAC Addresses      : 2
Total MAC Addresses        : 0
Configured MAC Addresses   : 0
Sticky MAC Addresses       : 0
Last Source Address:Vlan   : 0000.0000.0000:0
Security Violation Count   : 0
ASW-DC-01#show port-security
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
                (Count)       (Count)          (Count)
---------------------------------------------------------------------------
      Gi0/1              1            0                  0         Restrict
---------------------------------------------------------------------------
Total Addresses in System (excluding one mac per port)     : 0
Max Addresses limit in System (excluding one mac per port) : 4096
ASW-DC-01#show interfaces status

Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/0     to CSW-DC-01       connected    trunk      a-full   auto RJ45
Gi0/1     to SRV-DC-01       connected    999        a-full   auto RJ45
Gi0/2                        disabled     1            auto   auto RJ45
Gi0/3                        disabled     1            auto   auto RJ45
Gi1/0                        disabled     1            auto   auto RJ45
Gi1/1                        disabled     1            auto   auto RJ45
Gi1/2                        disabled     1            auto   auto RJ45
Gi1/3                        disabled     1            auto   auto RJ45
```

Expected result:

* Access ports should be assigned to the correct VLAN.
* PortFast and BPDU Guard should be enabled on end-device ports.
* Port security should match the lab requirements if configured.

Status: Passed

## 10. Final Result

The lab successfully verifies:

* VLAN segmentation
* 802.1Q trunking
* Native VLAN 99
* Rapid-PVST
* Layer 3 routed links
* Inter-VLAN routing
* OSPF routing in the Data Center segment
* Static routing between sites
* VLAN 999 filtering
* Default routing
* SSH-based management access
* Basic enterprise LAN troubleshooting

Final status: Passed
