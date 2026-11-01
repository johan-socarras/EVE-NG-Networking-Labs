# TSH-01 — Verification

This is the acceptance test for the lab: every check below has a command and a
value it has to return. It serves two purposes — proving the lab was built
correctly, and telling you when an incident is actually closed.

> **Measured on 2026-10-26**, on the healthy network and before any fault was
> injected (EVE-NG 6.2.0-4, IOSv 15.9(3)M4, IOSvL2 15.2, VPCS). The "Expected"
> column is the contract. Where the build taught something the design did not
> predict, the check says so, and everything that was measured is collected in
> [Measured results](#measured-results) at the end. The restored baseline itself
> is not published.

An incident is closed when **all** of it passes — not when the ping in the ticket
starts working. Faults are injected in groups, and a fix that restores one path
while leaving redundancy broken is the most common way to think you are done and
not be.

---

## 1 · Nodes and base state

| Check | Command | Expected |
|---|---|---|
| Every node booted with its own configuration | console prompt on each node | 23 nodes, each with its own hostname — never `Switch>`, `Router>` or `VPCS>` |
| Interfaces match the plan | `show ip interface brief \| exclude unassigned` | Every address in [`addressing-plan.md`](addressing-plan.md), all `up/up` |
| No SVI came up broken | `show ip interface brief \| include Vlan` | Every SVI `up/up`. An SVI whose `Method` is `TFTP` and which sits `down/down` is the known EVE-NG injection fault: delete and recreate it |
| Unused ports stay down | `show interfaces status \| include disabled` | Only the ports marked `UNUSED` in the skeleton configs |

## 2 · Layer 2

| Check | Command | Expected |
|---|---|---|
| VLANs exist on every switch of the site | `show vlan brief` | HQ: 10, 20, 30, 999 · BR: 110, 120, 130, 999 · DR: 210, 220, 230 |
| VTP is consistent | `show vtp status` | One domain per site, `DIST-A` server, everything else client, same revision on every switch of the site |
| Trunks are trunks | `show interfaces trunk` | Every access-to-distribution bundle and the distribution trunk in `trunking`, native VLAN 1, allowed list exactly the site's VLANs |
| No trunk ended up as an access port | `show interfaces switchport \| include Name\|Operational Mode` | No bundle member in `static access` |
| EtherChannels are up | `show etherchannel summary` | 11 bundles, 22 member ports, every bundle `(SU)` with its members `(P)` |
| LACP negotiated, or the fallback is recorded | `show lacp neighbor` | A neighbour on each bundle. If empty and the bundle is `(SD)`, the bundle is static `mode on` — write that here, with the date. **Measured: LACP negotiated on all 11 bundles, no fallback was needed** |
| Spanning tree roots are where they belong | `show spanning-tree vlan <id> \| include Root ID\|This bridge` | HQ: DIST-A root for 10 and 30, DIST-B for 20 · BR: DIST-A for 110 and 130, DIST-B for 120 · DR: DR-DIST-A for 210, 220, 230 |
| Mode is Rapid-PVST everywhere | `show spanning-tree summary \| include mode` | `rapid-pvst` on all ten switches |
| User ports are protected | `show spanning-tree interface <port> portfast`, `show port-security` | PortFast and BPDU guard on the nine access ports; port security max 1, dynamic, `violation shutdown`, zero violations |

## 3 · First-hop redundancy

| Check | Command | Expected |
|---|---|---|
| HSRP groups are complete | `show standby brief` | Six groups: HQ 10, 20, 30 and BR 110, 120, 130. Each with one `Active` and one `Standby`, never two actives |
| The right switch is active | `show standby brief` | HQ-DIST-A active for 10 and 30, HQ-DIST-B for 20 · BR-DIST-A active for 110 and 130, BR-DIST-B for 120 |
| Version and preemption | `show standby \| include version\|Preemption` | Version 2 and preemption enabled on all twelve group instances |
| DR has no FHRP, by design | `show standby brief` on DR-DIST-A | Empty. The `.1` addresses at DR are the switch's own SVIs |

## 4 · Routing

| Device | Command | Expected neighbours |
|---|---|---:|
| R1-HQ | `show ip ospf neighbor` | 4 — R2-BR, R3-DR, HQ-DIST-A, HQ-DIST-B |
| R2-BR | `show ip ospf neighbor` | 4 — R1-HQ, R3-DR, BR-DIST-A, BR-DIST-B |
| R3-DR | `show ip ospf neighbor` | 3 — R1-HQ, R2-BR, DR-DIST-A |
| HQ-DIST-A / HQ-DIST-B | `show ip ospf neighbor` | 2 each — the site router and the other distribution switch over VLAN 999 |
| BR-DIST-A / BR-DIST-B | `show ip ospf neighbor` | 2 each |
| DR-DIST-A | `show ip ospf neighbor` | 1 — R3-DR |

Ten adjacencies in total, every one in `FULL` (twenty ends). The `/30` links keep
the default OSPF network type, so each end reads `FULL/DR` or `FULL/BDR`. Anything
in `EXSTART`, `INIT` or `2WAY` on one of them is a fault, not a phase.

| Check | Command | Expected |
|---|---|---|
| Areas are right | `show ip ospf interface brief` | Area 0 only on the WAN links and router loopbacks; each site's interfaces in its own area |
| Authentication is on | `show ip ospf interface <link> \| include authentication\|Message digest` | Message-digest authentication on every adjacency, key 1 |
| User VLANs are passive | `show ip protocols \| section Passive` | Every user VLAN SVI listed; no transit link listed |
| Router IDs are pinned | `show ip ospf \| include ID` | The Loopback0 address of each device |
| Every site sees every other | `show ip route ospf` | All nine VLAN subnets, all loopbacks, both alternate WAN paths present as inter-area routes |
| The default route is tracked | `show ip sla statistics`, `show track 1`, `show ip route 0.0.0.0` | SLA returning, track `Reachability Up`, one static default on R1-HQ, and an `O*E2` default on every other device |

## 5 · Services

| Check | Command | Expected |
|---|---|---|
| Every DHCP client got a lease | `show ip dhcp binding` on each site router | Six leases: PC-HQ-1, PC-HQ-2 in `10.10.10.0/24`; PC-BR-1, PC-BR-2 in `10.20.10.0/24`; GUEST-BR-1 in `10.20.20.0/24`; PC-DR-1 in `10.30.10.0/24`. All at `.21` or above |
| Leases carry the right options | `show ip dhcp binding`, `ip` on the VPCS host | Gateway = the `.1` of the VLAN, DNS = `10.222.0.1` |
| The relay is in place | `show running-config interface Vlan<id> \| include helper` | `ip helper-address` on the four SVIs with pools, pointing at the site router's Loopback0 |
| Server VLANs answer no DHCP | `dhcp` from a VPCS in VLAN 20 or 220 | No lease. A lease there means a pool that should not exist |
| DNS resolves | `ping server01.corp.local` from R2-BR, `show hosts` | Resolves to `10.10.20.50` and replies |
| DNS is what clients were told | `ping dns01.corp.local` | Resolves to `10.222.0.1` |
| VPCS name resolution | `ping server01.corp.local` from PC-HQ-1 | VPCS resolves through the DNS it got from DHCP: `server01.corp.local resolved to 10.10.20.50`, then the ping replies (measured) |

## 6 · End-to-end connectivity

Run from the VPCS hosts, not from the switches: a switch has routes a user does
not.

| From | To | Expected |
|---|---|---|
| Every host | its own gateway `.1` | reply |
| PC-HQ-1 | `10.10.20.50` (same-site server, other VLAN) | reply |
| PC-HQ-1 | `10.30.20.50` (server at DR, across the WAN) | reply |
| PC-BR-1 | `10.10.20.50` and `10.30.20.50` | reply to both |
| PC-DR-1 | `10.10.20.50` | reply |
| Every user host | `203.0.113.1` (the Internet, through PAT) | reply |
| GUEST-BR-1 | `203.0.113.1` | reply — guests do get out |

## 7 · Policy: the tests that must fail

A lab where everything passes has not been checked.

| From | To | Expected |
|---|---|---|
| GUEST-BR-1 | `10.10.20.50` or `10.30.20.50` | **no reply** — guest traffic is denied inward |
| GUEST-BR-1 | `ping server01.corp.local` | the name **resolves** (DNS is the documented exception) and the ping then gets *administratively prohibited* from the distribution switch. A plain ICMP ping to `10.222.0.1` is denied too: only DNS is excepted |
| a user VLAN | SSH to a distribution switch's management address | **refused** — user VLANs are not in the VTY access-class. VPCS has no SSH client, so run it from a distribution switch, sourced from the SVI of the VLAN under test: `ip ssh source-interface Vlan10`, then `ssh -l netadmin 10.10.30.3`. The connection is closed with no password prompt, and `show ip access-lists MGMT_VTY` counts the deny |
| a MGMT VLAN | the same SSH, with `ip ssh source-interface Vlan30` (or `Vlan130`) | accepted: the banner and the `Password:` prompt appear (measured from `Vlan30` and `Vlan130`, and refused from `Vlan10` and `Vlan120`) |

| Check | Command | Expected |
|---|---|---|
| The ACLs are being hit | `show access-lists` | Non-zero counters on both the permit and the deny lines exercised above |
| Denies are logged | `show logging \| include list` | The guest deny visible in the buffer |

## 8 · NAT

| Check | Command | Expected |
|---|---|---|
| Translations exist | `show ip nat translations` | Entries from the site subnets, all translated to `192.0.2.1` |
| Counters move | `show ip nat statistics` | Hits increasing, misses flat while a ping runs |
| Inside and outside are on the right ports | `show ip nat statistics \| include interfaces` | Outside `Gi0/0` only; inside `Gi0/1` to `Gi0/4`: the two WAN links **and** the two links to the HQ distribution switches. The WAN links must be inside because Branch and DR reach the Internet through R1-HQ; a link that is not inside lets the traffic leave untranslated |
| The ISP cannot see inside | `ping 10.10.20.50` from ISP-1 | **no reply** — ISP-1 has no route into `10.0.0.0/8` and must not need one |

## 9 · Failure tests

Each one is run, measured, and then restored before the next. Remember that
EVE-NG links are bridges: shutting an interface on one side leaves the far side
`up/up`, so failures have to be created on the side being tested, and protocol
timers — not link state — are what does the detection.

| Test | How | Expected |
|---|---|---|
| Gateway failover | `shutdown` the active HSRP SVI at HQ (`interface Vlan10` on HQ-DIST-A) | Standby takes over, users keep pinging with at most a few lost packets, and it preempts back on restore |
| EtherChannel member loss | `shutdown` one member of an access bundle, on both ends | Bundle stays `(SU)` with one `(P)` member; a few packets are lost until both ends have noticed |
| Access uplink loss | `shutdown` an entire bundle on an access switch | Traffic reconverges over the other distribution switch; spanning tree unblocks the alternate path |
| WAN link loss | `shutdown` R1-HQ Gi0/1 | HQ still reaches BR, the long way round through R3-DR; OSPF routes shift and come back |
| Distribution uplink loss | `shutdown` HQ-DIST-A Gi0/0 | HQ-DIST-A keeps a path through the VLAN 999 transit to HQ-DIST-B — this is what that link exists for |
| Internet loss | `shutdown` ISP-1 Gi0/0 | The IP SLA probe fails, the track goes down, the static default is withdrawn and the `O*E2` default disappears everywhere instead of black-holing |

## 10 · Closing an incident

| Check | Expected |
|---|---|
| Sections 1 to 8 all pass | Yes, in one pass, with nothing skipped |
| The faults that were found are named | One line each: device, what was wrong, how it was found, what fixed it |
| Nothing was redesigned | The running configuration still matches [`addressing-plan.md`](addressing-plan.md). An address changed to make a ping work is a new fault, not a fix |
| Redundancy was not sacrificed | Section 9 still passes after the repairs |

---

## Measured results

Taken on the healthy network on 2026-10-26, from the consoles of the running lab.
178 checks were run by script (sections 1 to 8, plus the six tests of section 9
by hand); every one passed.

| Check | Measured |
|---|---|
| Nodes booted with their own hostname | 23 of 23 (14 qemu, 9 VPCS) |
| SVIs | all `up/up`, `Method manual` (created by hand; see the README on first-boot effects) |
| VLANs | present on every switch of each site; VTP v2, one domain per site, DIST-A server, revision HQ 5 · BR 5 · DR 4, equal inside each site |
| EtherChannels | 11 bundles, 22 members; seen from both ends: 22 × `Po(SU)` `LACP`, 44 × `(P)` |
| Trunks | every bundle `trunking`, native VLAN 1, allowed list exactly the site's VLANs (plus 999 on the distribution trunk) |
| Spanning tree | Rapid-PVST on all ten switches; roots: HQ DIST-A 10 and 30, DIST-B 20 · BR DIST-A 110 and 130, DIST-B 120 · DR-DIST-A 210, 220, 230 |
| User ports | nine access ports with PortFast, BPDU guard, port security max 1, `violation shutdown`, zero violations; unused ports disabled |
| HSRP | six groups, one `Active` and one `Standby` each, right switch active, version 2 and preempt on all twelve instances; DR-DIST-A has none |
| OSPF | R1-HQ 4, R2-BR 4, R3-DR 3, each distribution switch 2, DR-DIST-A 1: ten adjacencies, all `FULL`; areas 0 on the WAN and router loopbacks, 1 / 2 / 3 per site; cryptographic authentication on every adjacency; router IDs = Loopback0 |
| Routing table | every router and distribution switch sees the nine VLAN subnets; `O*E2 0.0.0.0/0` on every device except R1-HQ, whose default is static and tracked (`track 1` Up) |
| DHCP | six leases, all at `.21` or `.22`: PC-HQ-1 `10.10.10.21`, PC-HQ-2 `10.10.10.22`, PC-BR-1 `10.20.10.21`, PC-BR-2 `10.20.10.22`, GUEST-BR-1 `10.20.20.21`, PC-DR-1 `10.30.10.21`; gateway = the VLAN's `.1`, DNS `10.222.0.1`; the server VLAN answers no DHCP |
| DNS | `server01.corp.local` and `dns01.corp.local` resolve from R2-BR and reply; VPCS resolves them too |
| Connectivity | every host replies from its gateway; PC-HQ-1 → both servers, PC-BR-1 → both servers, PC-DR-1 → `10.10.20.50`, and all six user hosts (guest included) → `203.0.113.1` |
| Policy | GUEST-BR-1 gets no reply from either server; its DNS lookup works; `GUEST_IN` counters on permit and deny lines; the guest deny is in the log; SSH refused from `Vlan10` and `Vlan120`, accepted from `Vlan30` and `Vlan130` |
| NAT | translations from all three subnets to `192.0.2.1`; ISP-1 gets no reply from `10.10.20.50` |

Failure tests (section 9), ping from a VPCS host at one packet per second, each
test restored before the next:

| Test | Ping | Replies | Lost |
|---|---|---:|---:|
| Gateway failover: `interface Vlan10` shut on the active HQ-DIST-A | PC-HQ-1 → `10.10.20.50` | 28 of 30 | 2 |
| EtherChannel member: `Gi0/0` of HQ-ACC-1 and `Gi0/3` of HQ-DIST-A shut | PC-HQ-1 → `10.10.20.1` | 33 of 40 | 7 |
| Access uplink: `Port-channel1` shut on HQ-ACC-1 | PC-HQ-1 → `10.10.20.50` | 60 of 60 | 0 |
| WAN link: `Gi0/1` shut on R1-HQ | PC-HQ-1 → PC-BR-1 | 87 of 90 | 3 |
| Distribution uplink: `Gi0/0` shut on HQ-DIST-A | PC-HQ-1 → `203.0.113.1` | 57 of 60 | 3 |
| Internet loss: `Gi0/0` shut on ISP-1 | PC-DR-1 → `203.0.113.1` | — | — |

On the last one `track 1` went `Down` within about 35 seconds, R1-HQ's static
default was withdrawn and R3-DR printed `% Network not in table` for
`0.0.0.0` instead of black-holing; with the interface restored the track came back
`Up` and the default returned.
