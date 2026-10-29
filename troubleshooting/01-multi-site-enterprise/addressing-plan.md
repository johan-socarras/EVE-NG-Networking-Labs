# TSH-01 — IP Addressing Plan

23 nodes · 40 links · 9 VLANs across three sites

Everything internal lives in `10.0.0.0/8`, split so that the block tells you what
a thing is. Anything representing the public Internet uses documentation-only
ranges (RFC 5737), so the lab is portable and can never collide with a real
network.

## Address blocks

| Block | Purpose |
|---|---|
| `10.222.0.0/24` | Loopback0 on every routed device — stable OSPF router IDs |
| `10.0.0.0/30` – `10.0.0.8/30` | WAN triangle between the three site routers |
| `10.0.1.0/24` | HQ routed links: router to distribution, and the distribution transit |
| `10.0.2.0/24` | Branch routed links |
| `10.0.3.0/24` | DR routed links |
| `10.10.0.0/16` | HQ user VLANs (`10.10.<vlan-group>.0/24`) |
| `10.20.0.0/16` | Branch user VLANs |
| `10.30.0.0/16` | DR user VLANs |
| `192.0.2.0/30` | Internet edge link, R1-HQ to ISP-1 (RFC 5737) |
| `203.0.113.0/24` | Simulated Internet: the ISP loopback (RFC 5737) |

## Loopbacks

| Device | Loopback0 | Role |
|---|---|---|
| R1-HQ | `10.222.0.1/32` | OSPF router ID · DNS server (`dns01.corp.local`) |
| R2-BR | `10.222.0.2/32` | OSPF router ID · branch DHCP server |
| R3-DR | `10.222.0.3/32` | OSPF router ID · DR DHCP server |
| HQ-DIST-A | `10.222.0.11/32` | OSPF router ID |
| HQ-DIST-B | `10.222.0.12/32` | OSPF router ID |
| BR-DIST-A | `10.222.0.21/32` | OSPF router ID |
| BR-DIST-B | `10.222.0.22/32` | OSPF router ID |
| DR-DIST-A | `10.222.0.31/32` | OSPF router ID |
| ISP-1 | `203.0.113.1/32` | The address that means "the Internet" in every test |

Access switches are pure Layer 2 and have no loopback. They are reached on their
management SVI.

## WAN triangle — OSPF area 0

| Subnet | Device A | Interface | IP | Device B | Interface | IP |
|---|---|---|---|---|---|---|
| `10.0.0.0/30` | R1-HQ | Gi0/1 | `.1` | R2-BR | Gi0/1 | `.2` |
| `10.0.0.4/30` | R2-BR | Gi0/2 | `.5` | R3-DR | Gi0/1 | `.6` |
| `10.0.0.8/30` | R3-DR | Gi0/2 | `.9` | R1-HQ | Gi0/2 | `.10` |

Three routers, three links: every site keeps a second path when one WAN link
fails. The routers are the area border routers of their own site.

## Interface names

IOSvL2 names its eight interfaces in two groups of four (`Gi0/0`–`Gi0/3`,
`Gi1/0`–`Gi1/3`). IOSv numbers them straight through (`Gi0/0`–`Gi0/7`), so the
fifth port of `R1-HQ` and `R2-BR` is `Gi0/4`, not `Gi1/0`.

## Site routed links

Each distribution switch has its own routed `/30` to the site router, on a
physical port with `no switchport`. The distribution pair also carries a routed
transit link inside VLAN 999 over the Layer 2 EtherChannel between them, so the
pair stays OSPF-adjacent when one of them loses its uplink.

| Subnet | Device A | Interface | IP | Device B | Interface | IP | Area |
|---|---|---|---|---|---|---|---:|
| `10.0.1.0/30` | R1-HQ | Gi0/3 | `.1` | HQ-DIST-A | Gi0/0 | `.2` | 1 |
| `10.0.1.4/30` | R1-HQ | Gi0/4 | `.5` | HQ-DIST-B | Gi0/0 | `.6` | 1 |
| `10.0.1.8/30` | HQ-DIST-A | Vlan999 | `.9` | HQ-DIST-B | Vlan999 | `.10` | 1 |
| `10.0.2.0/30` | R2-BR | Gi0/3 | `.1` | BR-DIST-A | Gi0/0 | `.2` | 2 |
| `10.0.2.4/30` | R2-BR | Gi0/4 | `.5` | BR-DIST-B | Gi0/0 | `.6` | 2 |
| `10.0.2.8/30` | BR-DIST-A | Vlan999 | `.9` | BR-DIST-B | Vlan999 | `.10` | 2 |
| `10.0.3.0/30` | R3-DR | Gi0/3 | `.1` | DR-DIST-A | Gi0/0 | `.2` | 3 |

## Internet edge

| Subnet | Device A | Interface | IP | Device B | Interface | IP |
|---|---|---|---|---|---|---|
| `192.0.2.0/30` | R1-HQ | Gi0/0 | `.1` | ISP-1 | Gi0/0 | `.2` |

R1-HQ is the only door to the outside. Its default route is static, tied to an IP
SLA probe against `203.0.113.1` with object tracking, and injected into OSPF with
`default-information originate`. The tracking is not decoration: EVE-NG links are
bridges and do not propagate link-down, so a dead upstream leaves the interface
`up/up` and an untracked static route would keep black-holing every site's
Internet traffic.

PAT translates every internal source to `192.0.2.1`. ISP-1 has no route back into
`10.0.0.0/8`, which is the point: if a test reaches `203.0.113.1`, the
translation worked.

`Gi0/0` is `ip nat outside`. `ip nat inside` is on the four links that face the
rest of the network: `Gi0/3` and `Gi0/4` toward the HQ distribution switches and
`Gi0/1` and `Gi0/2` toward the WAN. The WAN links have to be inside too: Branch
and DR reach the Internet through `R1-HQ`, and traffic that arrives on a link that
is not `inside` leaves untranslated and never comes back. The translation ACL,
`NAT_INSIDE`, permits `10.0.0.0/8`.

## VLANs, gateways and HSRP

`.1` is always the gateway. At HQ and Branch it is an HSRPv2 virtual address
shared by the two distribution switches; at DR, where there is a single
distribution switch, `.1` is that switch's own SVI.

### Headquarters — OSPF area 1

| VLAN | Name | Subnet | Gateway | HQ-DIST-A | HQ-DIST-B | HSRP active |
|---:|---|---|---|---|---|---|
| 10 | USERS | `10.10.10.0/24` | `.1` | `.2` prio 110 | `.3` prio 100 | HQ-DIST-A |
| 20 | SERVERS | `10.10.20.0/24` | `.1` | `.2` prio 100 | `.3` prio 110 | HQ-DIST-B |
| 30 | MGMT | `10.10.30.0/24` | `.1` | `.2` prio 110 | `.3` prio 100 | HQ-DIST-A |

### Branch office — OSPF area 2

| VLAN | Name | Subnet | Gateway | BR-DIST-A | BR-DIST-B | HSRP active |
|---:|---|---|---|---|---|---|
| 110 | USERS | `10.20.10.0/24` | `.1` | `.2` prio 110 | `.3` prio 100 | BR-DIST-A |
| 120 | GUEST | `10.20.20.0/24` | `.1` | `.2` prio 100 | `.3` prio 110 | BR-DIST-B |
| 130 | MGMT | `10.20.30.0/24` | `.1` | `.2` prio 110 | `.3` prio 100 | BR-DIST-A |

### Disaster recovery — OSPF area 3

| VLAN | Name | Subnet | Gateway | DR-DIST-A |
|---:|---|---|---|---|
| 210 | USERS | `10.30.10.0/24` | `.1` | `.1` — no HSRP |
| 220 | SERVERS | `10.30.20.0/24` | `.1` | `.1` — no HSRP |
| 230 | MGMT | `10.30.30.0/24` | `.1` | `.1` — no HSRP |

HSRP group numbers match the VLAN id, preemption is on for both peers, and the
spanning-tree root for a VLAN is pinned to the switch that is HSRP active for it,
so the forwarding path and the gateway agree instead of trombone-ing across the
distribution trunk.

VLAN 999 carries only the distribution transit link. VLAN 1 is unused: no SVI, no
access port, and it is the native VLAN on every trunk.

## Host addressing

| Host | Site | VLAN | Address | How |
|---|---|---:|---|---|
| PC-HQ-1 | HQ | 10 | `10.10.10.x` | DHCP |
| PC-HQ-2 | HQ | 10 | `10.10.10.x` | DHCP |
| SRV-HQ-1 | HQ | 20 | `10.10.20.50/24` | static, gateway `10.10.20.1` |
| PC-BR-1 | BR | 110 | `10.20.10.x` | DHCP |
| PC-BR-2 | BR | 110 | `10.20.10.x` | DHCP |
| GUEST-BR-1 | BR | 120 | `10.20.20.x` | DHCP |
| PC-DR-1 | DR | 210 | `10.30.10.x` | DHCP |
| SRV-DR-1 | DR | 220 | `10.30.20.50/24` | static, gateway `10.30.20.1` |
| MGMT-1 | DR | 230 | `10.30.30.50/24` | static, gateway `10.30.30.1` |

## Switch management addressing

| Switch | VLAN | Address | Default gateway |
|---|---:|---|---|
| HQ-DIST-A | 30 | `10.10.30.2/24` | routed device |
| HQ-DIST-B | 30 | `10.10.30.3/24` | routed device |
| HQ-ACC-1 | 30 | `10.10.30.11/24` | `10.10.30.1` |
| HQ-ACC-2 | 30 | `10.10.30.12/24` | `10.10.30.1` |
| BR-DIST-A | 130 | `10.20.30.2/24` | routed device |
| BR-DIST-B | 130 | `10.20.30.3/24` | routed device |
| BR-ACC-1 | 130 | `10.20.30.11/24` | `10.20.30.1` |
| BR-ACC-2 | 130 | `10.20.30.12/24` | `10.20.30.1` |
| DR-DIST-A | 230 | `10.30.30.1/24` | routed device |
| DR-ACC-1 | 230 | `10.30.30.11/24` | `10.30.30.1` |

Access switches are Layer 2 and reach the rest of the network through
`ip default-gateway`, which is the HSRP virtual address of their management VLAN.

## DHCP

Pools live on the site routers. The distribution SVIs relay to them with
`ip helper-address` pointed at the site router's Loopback0, which stays reachable
through OSPF no matter which uplink is up.

| Pool | Server | Network | Excluded | Gateway | DNS | Relay from |
|---|---|---|---|---|---|---|
| `HQ-USERS` | R1-HQ | `10.10.10.0/24` | `.1`–`.20` | `10.10.10.1` | `10.222.0.1` | HQ-DIST-A/B Vlan10 → `10.222.0.1` |
| `BR-USERS` | R2-BR | `10.20.10.0/24` | `.1`–`.20` | `10.20.10.1` | `10.222.0.1` | BR-DIST-A/B Vlan110 → `10.222.0.2` |
| `BR-GUEST` | R2-BR | `10.20.20.0/24` | `.1`–`.20` | `10.20.20.1` | `10.222.0.1` | BR-DIST-A/B Vlan120 → `10.222.0.2` |
| `DR-USERS` | R3-DR | `10.30.10.0/24` | `.1`–`.20` | `10.30.10.1` | `10.222.0.1` | DR-DIST-A Vlan210 → `10.222.0.3` |

The static hosts sit on `.50`, inside no pool, so a leased address and a hardcoded
one are never confused while troubleshooting. Server and management VLANs have no
pool on purpose: a DHCP request there should go unanswered.

## DNS

R1-HQ answers DNS for `corp.local` with `ip dns server`. There is no Linux image
in this lab, so the router plays the part a server would play in production; the
failure modes a student has to chase — wrong address handed out by DHCP, resolver
unreachable through an ACL — behave the same way.

| Name | Address | Host |
|---|---|---|
| `dns01.corp.local` | `10.222.0.1` | R1-HQ Loopback0 |
| `server01.corp.local` | `10.10.20.50` | SRV-HQ-1 |
| `server02.corp.local` | `10.30.20.50` | SRV-DR-1 |

## Access ports

| Switch | Port | VLAN | Host |
|---|---|---:|---|
| HQ-ACC-1 | Gi1/0 | 10 | PC-HQ-1 |
| HQ-ACC-1 | Gi1/1 | 20 | SRV-HQ-1 |
| HQ-ACC-2 | Gi1/0 | 10 | PC-HQ-2 |
| BR-ACC-1 | Gi1/0 | 110 | PC-BR-1 |
| BR-ACC-2 | Gi1/0 | 110 | PC-BR-2 |
| BR-ACC-2 | Gi1/1 | 120 | GUEST-BR-1 |
| DR-ACC-1 | Gi1/0 | 210 | PC-DR-1 |
| DR-ACC-1 | Gi1/1 | 220 | SRV-DR-1 |
| DR-ACC-1 | Gi1/2 | 230 | MGMT-1 |

Every port in this table carries PortFast, BPDU guard and port security with one
dynamically learned MAC address and `violation shutdown`. Sticky MAC addresses
are deliberately not used: a rebuilt VPCS node can come back with a different
MAC, and a lab that breaks itself on a reboot teaches the wrong lesson.

## EtherChannels

| Site | Bundle | Members | Between | Mode |
|---|---|---|---|---|
| HQ | Po1 | 2 | HQ-DIST-A ↔ HQ-DIST-B | trunk, `nonegotiate` |
| HQ | Po1 / Po2 | 2 each | HQ-ACC-1 ↔ each distribution switch | trunk |
| HQ | Po1 / Po2 | 2 each | HQ-ACC-2 ↔ each distribution switch | trunk |
| BR | Po1 | 2 | BR-DIST-A ↔ BR-DIST-B | trunk, `nonegotiate` |
| BR | Po1 / Po2 | 2 each | BR-ACC-1 ↔ each distribution switch | trunk |
| BR | Po1 / Po2 | 2 each | BR-ACC-2 ↔ each distribution switch | trunk |
| DR | Po1 | 2 | DR-ACC-1 ↔ DR-DIST-A | trunk |

Eleven bundles, twenty-two member links. Trunks allow only the VLANs of their own
site plus 999 where it applies.

Bundle numbering, the same at every site with two distribution switches:

| Switch | Po1 | Po2 | Po3 |
|---|---|---|---|
| DIST-A / DIST-B | the other distribution switch | ACC-1 | ACC-2 |
| ACC-1 / ACC-2 | DIST-A | DIST-B | — |

At DR, `DR-DIST-A` and `DR-ACC-1` use `Po1` for the only bundle. The members are
the ports whose description ends in `(POn_MEMBER)` in the skeleton configs.

DTP is left negotiating on the access-to-distribution bundles (`dynamic
desirable` on the distribution side, `dynamic auto` on the access side) and is off
on the distribution trunk (`switchport mode trunk` plus `nonegotiate`).

LACP was attempted first, and it negotiated on all eleven bundles on the EVE-NG
build used here (`show lacp neighbor` lists a partner on every bundle and every
bundle is `(SU)` with its members `(P)`). If yours comes up as `Po1(SD)` with the
members suspended and `show lacp neighbor` empty — which has happened on other
EVE-NG bridges — move the bundle to static `channel-group N mode on` and note it
in `verification.md`.

## VTP and spanning tree

VTPv2, one domain per site, named `HQ`, `BR` and `DR`. DIST-A of each site is the
server and creates the VLANs (and VLAN 999 where it applies); every other switch is
a client. Rapid-PVST everywhere. The root bridge of a VLAN is the switch that is
HSRP active for it: priority 4096 on that switch, 8192 on its peer (VLAN 999 is
8192 on both).

## Access control

| ACL | Where | What it does |
|---|---|---|
| `GUEST_IN` (extended) | `Vlan120` inbound on `BR-DIST-A` and `BR-DIST-B` | permits DHCP (client requests, and the relay replies from the site router `10.0.2.0/24` back to `10.20.20.0/24`), traffic inside the guest subnet and DNS to `10.222.0.1`, denies the rest of `10.0.0.0/8` with `log`, permits everything else (the Internet) |
| `MGMT_VTY` (standard) | `line vty 0 4` as `access-class … in`, on all 14 IOS devices | permits the three MGMT subnets (`10.10.30.0/24`, `10.20.30.0/24`, `10.30.30.0/24`) and the device loopbacks `10.222.0.0/24`; denies and logs the rest |
| `NAT_INSIDE` (standard) | `R1-HQ`, the `ip nat inside source list` | permits `10.0.0.0/8` |

The relay reply is in `GUEST_IN` for a reason: the reply to a guest's DHCP request
is addressed to the SVI of one distribution switch and can arrive through the
other one across VLAN 120, where an inbound ACL that only knew guest sources would
drop it.

## OSPF

| Area | Contents |
|---:|---|
| 0 | The three WAN links and the three router loopbacks |
| 1 | HQ: both router-to-distribution links, the distribution transit, HQ VLANs, HQ distribution loopbacks |
| 2 | Branch: the same shape |
| 3 | DR: the single router-to-distribution link, DR VLANs, DR distribution loopback |

Router IDs are the Loopback0 addresses. Every adjacency carries MD5
authentication — the key itself is not published. User VLAN interfaces are
passive: they are advertised, they do not look for neighbours. Expected adjacency
counts are in [`verification.md`](verification.md).
