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
ASW-DC-02#sh vlan brief

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
ASW-DC-02#show interfaces trunk

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
ASW-A-01#sh vlan brief

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
ASW-A-01#show interfaces trunk

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

```cisco
ASW-B-01#sh vlan brief

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
ASW-B-01#show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/0       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/0       10,20,30,99-100,999

Port        Vlans allowed and active in management domain
Gi0/0       10,20,30,99-100,999

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/0       10,20,30,99-100,999
```

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

'''cisco
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
'''

'''cisco
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
'''

'''cisco
ASW-DC-02#show spanning-tree summary
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
ASW-DC-02#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     5000.0006.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-DC-02#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32788  (priority 32768 sys-id-ext 20)
             Address     5000.0006.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-DC-02#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.0004.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32867  (priority 32768 sys-id-ext 99)
             Address     5000.0006.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p
'''

'''cisco
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

'''

'''cisco
ASW-A-01#show spanning-tree summary
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
ASW-A-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.000b.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     5000.000e.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-A-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.000b.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32788  (priority 32768 sys-id-ext 20)
             Address     5000.000e.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-A-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.000b.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32867  (priority 32768 sys-id-ext 99)
             Address     5000.000e.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p
'''

'''cisco
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
'''

'''cisco
ASW-B-01#show spanning-tree summary
Switch is in rapid-pvst mode
Root bridge for: VLAN0001
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
VLAN0001                     0         0        0          6          6
VLAN0010                     0         0        0          1          1
VLAN0020                     0         0        0          1          1
VLAN0030                     0         0        0          2          2
VLAN0099                     0         0        0          1          1

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0100                     0         0        0          1          1
VLAN0999                     0         0        0          2          2
---------------------- -------- --------- -------- ---------- ----------
7 vlans                      0         0        0         14         14
ASW-B-01#show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     5000.000c.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32778  (priority 32768 sys-id-ext 10)
             Address     5000.000d.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-B-01#show spanning-tree vlan 20

VLAN0020
  Spanning tree enabled protocol rstp
  Root ID    Priority    24596
             Address     5000.000c.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32788  (priority 32768 sys-id-ext 20)
             Address     5000.000d.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p


ASW-B-01#show spanning-tree vlan 99

VLAN0099
  Spanning tree enabled protocol rstp
  Root ID    Priority    24675
             Address     5000.000c.0000
             Cost        4
             Port        1 (GigabitEthernet0/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32867  (priority 32768 sys-id-ext 99)
             Address     5000.000d.0000
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Root FWD 4         128.1    P2p
'''

Status: Passed

## 3. Layer 3 Interface Verification

Commands used:

```cisco
show ip interface brief
show ip route connected
```

Expected result:

* Routed interfaces should be up/up.
* SVIs should be up/up for active VLANs.
* Connected routes should appear for local VLANs and point-to-point links.

Status: Passed / Pending

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

Status: Passed / Pending

## 5. Inter-Site Connectivity Tests

Test from Data Center to Site-A:

```bash
ping 10.1.99.10
```

Test from Data Center to Site-B:

```bash
ping 10.2.99.10
```

Test from Site-A to Site-B:

```bash
ping 10.2.99.10
```

Test from Site-B to Site-A:

```bash
ping 10.1.99.10
```

Expected result:

* Devices in different sites should be able to reach each other according to the routing design.

Status: Passed / Pending

## 6. Default Route Verification

Commands used:

```cisco
show ip route 0.0.0.0
show ip route
```

Expected result:

* Core switches should have a default route pointing toward the upstream router.
* Remote sites should have a valid path back to the Data Center and other site networks.

Status: Passed / Pending

## 7. Isolated VLAN Verification

Commands used:

```cisco
show access-lists
show running-config interface vlan 999
```

Connectivity tests from an isolated VLAN host:

```bash
ping <default-gateway>
ping <internal-site-network>
ping <allowed-external-destination>
```

Expected result:

* VLAN 999 should be restricted by ACL.
* The isolated VLAN should not have unrestricted access to internal private networks.
* Allowed traffic should work according to the ACL design.

Status: Passed / Pending

## 8. SSH Management Verification

Commands used:

```cisco
show ip ssh
show running-config | section line vty
```

SSH test:

```bash
ssh admin@<device-management-ip>
```

Expected result:

* SSH version 2 should be enabled.
* VTY lines should use local login.
* Remote access should be limited to SSH.

Status: Passed / Pending

## 9. Port Security / Access Port Verification

Commands used:

```cisco
show port-security
show port-security interface gigabitEthernet0/1
show interfaces status
```

Expected result:

* Access ports should be assigned to the correct VLAN.
* PortFast and BPDU Guard should be enabled on end-device ports.
* Port security should match the lab requirements if configured.

Status: Passed / Pending

## 10. Final Result

The lab successfully verifies:

* VLAN segmentation
* 802.1Q trunking
* Native VLAN 99
* Rapid-PVST
* Layer 3 routed links
* Inter-VLAN routing
* OSPF routing between sites
* Default routing
* Isolated VLAN filtering
* SSH-based management access
* Basic enterprise LAN troubleshooting

Final status: Passed / Pending
