# Verification — Lab 02

Run these in order. Each step assumes the previous one passed; if one fails,
fix it before moving on, because later checks depend on it.

Console ports are assigned by EVE-NG in node order, starting at 32769:
`ISP-1 32769, ISP-2 32770, C-SW-1 32771, C-SW-2 32772, D-SW-1 32773,
D-SW-2 32774, A-SW-1..4 32775-32778, PC-1..8 32779-32786`. Reaching them with
`telnet <eve-ip> <port>` is often quicker than the HTML5 console.

## 0. Nodes booted with their configuration

```
show running-config | include hostname
```

Expected: the device's own hostname. A node answering `Switch>` booted with the
factory config — EVE-NG only injects the startup-config into a node that boots
clean. Stop it, **Wipe** it, start it again.

If a node refuses to start at all (EVE-NG reports "started" but no qemu process
appears and the console port stays closed), wipe it too. A node that keeps
failing after a wipe can be deleted and recreated; the point-to-point networks
survive the deletion, so the replacement only needs its interfaces reconnected.
Note that a recreated node reusing the same node ID also reuses the old working
directory — wipe it once more after recreating it.

## 1. Addressing and interface state

On each Core and Distribution device:

```
show ip interface brief | exclude unassigned
```

Expected — every listed interface `up/up`, matching
[`addressing-plan.md`](addressing-plan.md):

| Device | Expected |
|---|---|
| C-SW-1 | `Gi0/0 192.0.2.1`, `Gi0/1 10.0.0.1`, `Gi0/2 10.0.0.5`, `Gi0/3 10.0.0.21`, `Lo0 10.222.0.1` |
| C-SW-2 | `Gi0/0 198.51.100.1`, `Gi0/1 10.0.0.13`, `Gi0/2 10.0.0.9`, `Gi0/3 10.0.0.22`, `Lo0 10.222.0.2` |
| D-SW-1 | `Gi0/2 10.0.0.2`, `Gi0/3 10.0.0.10`, `Lo0 10.222.0.3`, plus `Vlan10/20/30/40` |
| D-SW-2 | `Gi0/2 10.0.0.14`, `Gi0/3 10.0.0.6`, `Lo0 10.222.0.4`, plus `Vlan10/20/30/40` |

An interface showing `administratively down` is missing its `no shutdown`. One
that is `up/down` is cabled to the wrong peer — check the interface map.

## 2. EtherChannel between the Distribution switches

```
show etherchannel summary
```

Expected: `Po1(SU)` with `Gi0/0(P)` and `Gi0/1(P)`. `S` = Layer 2, `U` = in use,
`(P)` = bundled.

- `(I)` on a member means it is standalone — LACP is not negotiating. Confirm
  both ends use `channel-group 1 mode active`.
- `Po1(SD)` means the bundle is down: usually the trunk settings differ between
  the two members.

`Po1` must carry **no** IP address and **no** OSPF. If `show ip interface brief`
lists an address on it, that is a deviation from the design.

## 3. OSPF adjacencies

```
show ip ospf neighbor
```

Expected across the whole lab: **five adjacencies**, all `FULL`.

| Area | Adjacency |
|---|---|
| 0 | C-SW-1 ↔ C-SW-2 |
| 1 | C-SW-1 ↔ D-SW-1 |
| 1 | C-SW-1 ↔ D-SW-2 |
| 1 | C-SW-2 ↔ D-SW-1 |
| 1 | C-SW-2 ↔ D-SW-2 |

So each Core sees **three** neighbours and each Distribution sees **two**.

The transit links use `ip ospf network point-to-point`, so the `State` column
shows `FULL/  -` rather than `FULL/DR` — that is correct, not a fault.

More than five means something that should be passive is not — most likely an
SVI, or OSPF enabled on `Po1`. Fewer means a link is down or one side is missing
its `ip ospf 1 area <n>`.

Confirm the Core devices are ABRs:

```
show ip ospf | include Area|border
```

Expected on C-SW-1 and C-SW-2: area border router, attached to areas 0 and 1.

## 4. Routing table

On C-SW-1:

```
show ip route ospf
```

Expected: the four user VLANs (`10.10.10.0/24` … `10.10.40.0/24`), the two
transit `/30`s it does not own (`10.0.0.8/30`, `10.0.0.12/30`) and the three
other loopbacks.

Only the **four VLANs** show two equal-cost paths — one via each Distribution
switch, both at cost 2. Everything else has a single best path, and that is
correct, not a fault: each Distribution loopback is one hop away over its own
transit link (cost 2 versus 4 the long way round); each remote `/30` is reached
through the Distribution switch that terminates it (cost 2 versus 3); and
`10.222.0.2/32` sits in area 0, so its only intra-area path is the Core–Core
link — OSPF never load-shares an intra-area route with an inter-area one.

A VLAN with only one path means a Core–Distribution link is down; the lab still
works, but it no longer demonstrates the redundancy it exists to show.

## 5. HSRP

On D-SW-1 and D-SW-2:

```
show standby brief
```

Expected — the active router alternates by VLAN, and each VIP is `.1`:

| Group | VIP | Active | Standby |
|---|---|---|---|
| 10 | `10.10.10.1` | D-SW-1 | D-SW-2 |
| 20 | `10.10.20.1` | D-SW-2 | D-SW-1 |
| 30 | `10.10.30.1` | D-SW-1 | D-SW-2 |
| 40 | `10.10.40.1` | D-SW-2 | D-SW-1 |

Both switches showing `Active` for the same group means they cannot hear each
other — check `Po1` and that both trunks allow the VLAN.

## 6. End-to-end connectivity

From PC-1 (for another host, substitute its own gateway and a host in a
different VLAN):

```
show ip
ping 10.10.10.1
ping 10.10.10.101
ping 10.10.20.100
ping 203.0.113.1
ping 203.0.113.2
```

Expected: the host has its planned address and gateway; the gateway replies;
its neighbour in the same VLAN replies (the access switch works); a host in
another VLAN replies (inter-VLAN routing works); and **both** ISP loopbacks reply
(the campus can reach the Internet through either upstream).

Ping both `203.0.113.1` and `203.0.113.2`, not just one. The two Core devices
load-share the default route, so a single destination only exercises one of the
two upstreams and can pass while the other path is broken.

The first packet of a run often times out while ARP resolves. Two replies out of
three is a pass; zero is a failure.

Measured on the finished lab, three pings per destination from every host:
gateway, same-VLAN neighbour, a host in another VLAN and `203.0.113.1` — 8 hosts
× 4 destinations = 32 checks, no failures. `203.0.113.2` was then confirmed from
PC-1 separately, and again from PC-1 during the upstream failure test below.

`trace 203.0.113.1` from PC-1 should show the HSRP active switch for VLAN 10,
then a Core, then an ISP.

## 7. Failure tests — the point of the lab

Run these with a continuous ping going from PC-1. Restore each one before moving
to the next, and do **not** save while an interface is shut.

### The HSRP active router fails

```
D-SW-1(config)# interface Vlan10
D-SW-1(config-if)# shutdown
```

Expected: `show standby brief` on D-SW-2 flips VLAN 10 to `Active`, and traffic
from PC-1 keeps flowing. Measured: no packet loss at all. Undo the shutdown and,
because preemption is configured, D-SW-1 reclaims the active role.

### A Core–Distribution link fails

```
D-SW-1(config)# interface GigabitEthernet0/2
D-SW-1(config-if)# shutdown
```

Expected: D-SW-1 drops from two OSPF neighbours to one, reconverges over `Gi0/3`
toward C-SW-2, and traffic keeps flowing. Measured: no loss during the failure,
occasionally one packet on the way back as OSPF reconverges.

### An EtherChannel member fails

```
D-SW-1(config)# interface GigabitEthernet0/0
D-SW-1(config-if)# shutdown
```

Expected: `show etherchannel summary` shows `Po1(SU)` still up, with `Gi0/0(D)`
and `Gi0/1(P)`. HSRP does not flap and traffic keeps flowing.

### An upstream ISP fails

```
ISP-1(config)# interface GigabitEthernet0/0
ISP-1(config-if)# shutdown
```

Expected: within about 15 seconds `show track 1` reads `Down` on both C-SW-1 and
ISP-1; C-SW-1 withdraws its default route and stops advertising it into OSPF, so
the campus leaves through C-SW-2. **Both** `203.0.113.1` and `203.0.113.2` stay
reachable — `.2` directly through ISP-2, and `.1` through ISP-2 and the peering
link, with ISP-1 answering over its floating return route. Measured: no loss to
either destination.

This is the test that justifies the peering link and the IP SLA probes. Before
they existed it failed in two different ways: traffic to the "wrong" ISP died
there, and once an upstream went down the Core kept advertising a default route
into a black hole, because an EVE-NG bridge never signals link-down to the far
end.
