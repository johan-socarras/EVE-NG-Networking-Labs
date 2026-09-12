# Lab 01 — Collapsed-Core Enterprise LAN

Three sites, seven VLANs, and a WAN triangle that survives losing a link. Each
site is a self-contained routing domain; the sites are stitched together by
summarised static routes that are withdrawn automatically when the far end stops
answering.

- **Lab file:** not distributed — see *Running the lab*
- **Platform:** EVE-NG Community
- **Images:** `vios-adventerprisek9` (routers), `viosl2-adventerprisek9` (switches), VPCS (endpoints)
- **Size:** 14 nodes, 18 links, 7 VLANs, 10 QEMU nodes

## Topology

![Topology](topology.png)


## About the name

The folder is called `01-three-tier-enterprise-lan` for link stability — it is
referenced from outside this repository — but the lab is **not** three-tier and
does not claim to be. The real chain is **access switch → site multilayer switch
→ site router**: a collapsed core, with no separate distribution layer. An
earlier revision of this lab called itself three-tier while implementing exactly
this; the design did not change, the description did.

## Layers

**Site router — `RTR-DC-01`, `RTR-A-01`, `RTR-B-01`.** IOSv routers, fully
meshed in a triangle over `172.16.0.0/28`. Each one is the OSPF edge of its site,
the DHCP server for its own user VLANs, and the owner of the static routes toward
the other two sites.

**Site multilayer — `CSW-DC-01`, `CSW-A-01`, `CSW-B-01`.** IOSvL2 switches doing
both distribution and core. Northbound they are routed (`no switchport` on
`Gi0/0`) and speak OSPF with their site router. Southbound they are 802.1Q
trunks over EtherChannel toward the access switches. They own every SVI, so all
inter-VLAN routing happens here.

**Access — `ASW-DC-01`, `ASW-DC-02`, `ASW-A-01`, `ASW-B-01`.** Pure Layer 2
(`no ip routing`), one endpoint each, dual-link EtherChannel uplink, and a
management SVI in VLAN 10 so they can actually be administered over SSH.

## VLANs

| VLAN | Name | Subnet | Gateway | Notes |
|---|---|---|---|---|
| 10 | Management | `10.N.10.0/24` | `.1` | Switch management, and the only source allowed on the VTY lines |
| 20 | Data | `10.N.20.0/24` | `.1` | Addressed by DHCP relay |
| 30 | Voice | `10.N.30.0/24` | `.1` | Addressed by DHCP relay, option 150 set for phones |
| 99 | Native-Trunk | — | — | Trunk native VLAN, deliberately unaddressed |
| 100 | Server | `10.N.100.0/24` | `.1` | Routed and reachable; no endpoint is connected in this lab |
| 199 | Isolated-Lab | `10.N.199.0/24` | `.1` | Filtered in both directions, see below |
| 1000 | Unused-Parking | — | — | Where every unused access port is shut and parked |

`N` is `0` for Site-DC, `1` for Site-A and `2` for Site-B. Every subnet's third
octet is its VLAN ID, with no exceptions — which is why the isolated VLAN is 199
and not 999: at 999 the only subnet that fits is `10.N.99.0/24`, which reads
exactly like the native VLAN and makes `ip route 10.0.99.0` ambiguous.

## Design decisions worth knowing

**OSPF stays inside each site.** Process 1, area 0, three adjacencies — one per
site, between the router and its multilayer switch. Interfaces are placed with
`ip ospf 1 area 0`, the transit link runs `ip ospf network point-to-point`, and
`passive-interface default` means the SVIs are advertised without sending hellos
into user VLANs. Every adjacency is authenticated with MD5. Router IDs are
pinned to a Loopback0 so they cannot drift when an interface changes.

**Loopbacks live inside their own site's /16.** `10.N.255.1` for the router,
`10.N.255.2` for the multilayer switch. That is not cosmetic: it means the
per-site summary route below already covers them, and no extra route is needed to
reach a device's stable address from another site.

**Inter-site routing is summarised, tracked, and backed up.** Each router holds
four static routes instead of one per remote VLAN: a `/16` per remote site,
primary via the direct link and tied to an IP SLA probe, plus a floating route
(distance 100) via the third side of the triangle.

```
ip sla 1
 icmp-echo 172.16.0.1 source-interface GigabitEthernet0/1
 frequency 5
ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability
ip route 10.0.0.0 255.255.0.0 172.16.0.1 track 1
ip route 10.0.0.0 255.255.0.0 172.16.0.10 100
```

The `/16` is what makes the transit `/30`s reachable from the other sites — a
previous revision routed each remote VLAN individually, so the point-to-point
links themselves were unreachable and inter-site `traceroute` died one hop short.

**The tracking is not decoration.** EVE-NG links are Linux bridges and a bridge
does not propagate link-down: shutting an interface at one end leaves the far end
`up/up`, the connected route stays in the table and a plain static route is never
invalidated. Without IP SLA the failure test cannot pass, and the failure looks
like a design bug when it is a simulator artefact.

**VLAN 199 is filtered in both directions.** Two ACLs on the SVI, not one:

```
ip access-list extended ISOLATED-IN
 permit icmp 10.0.199.0 0.0.0.255 10.0.199.0 0.0.0.255
 permit icmp 10.0.199.0 0.0.0.255 10.1.199.0 0.0.0.255
 permit icmp 10.0.199.0 0.0.0.255 10.2.199.0 0.0.0.255
 deny   ip any any log
```

The outbound list mirrors it and additionally permits `ttl-exceeded` and
`unreachable`, so path errors still reach the host and `traceroute` from an
isolated endpoint remains usable. An inbound-only list, as an earlier revision
had, filters what leaves the VLAN and nothing that enters it.

**Every user VLAN gets its address from its own site router.** `ip helper-address`
on the VLAN 20 and 30 SVIs points at the site router's loopback, and the pools
live on the router. `SRV-DC-02` is a DHCP client precisely so this is
demonstrable rather than merely configured.

## Platform notes

Both of these are limitations of the images, not of the design, and both are
stated here rather than hidden.

**EtherChannel is static, because LACP does not negotiate over EVE-NG bridges.**
Configured with `channel-group N mode active` on both ends, every bundle stayed
`Po1(SD)` with its members suspended and `show lacp neighbor` empty on both
sides. The same links carry STP BPDUs and CDP fine, and the bundles come up
immediately with `mode on`. LACP frames use the slow-protocols multicast address
and do not cross. See [`verification.md`](verification.md) §10.

**SSH MAC algorithms are hardened on the routers only.** `ip ssh server algorithm
mac hmac-sha2-256 hmac-sha2-512` is accepted by IOSv 15.9 but not implemented by
IOSvL2 15.2, so the seven switches keep the platform default. Everything else —
SSHv2, AES-CTR ciphers, a 2048-bit DH minimum and a 2048-bit host key — is
applied on all ten devices.

## Known limitation

Floating static routes on a triangle have one failure mode that this lab does not
solve: if an **entire site router** goes away — not a link — the two remaining
routers each fall back to their floating route, which points at the other, and
packets for that site loop until the TTL expires. Losing a **link**, which is
what the failure test exercises, reconverges correctly and without loss.

Fixing it properly means running a routing protocol across the WAN instead of
static routes. That is deliberately left as the difference between this lab and
[Lab 02](../02-three-tier-architecture/README.md), which is OSPF end to end.

## What is in `configs/`

`configs/` holds what each device actually runs, pulled from the lab itself and
sanitised. Secrets are replaced by a fixed-length `<REDACTED>` marker — never by
a run of asterisks matching the original length, which leaks exactly how long
each credential was.

[`configs-skeleton/`](configs-skeleton/) is the other half: the clean starting
point for every device, with hostnames, interface descriptions, routed
addressing and loopbacks, and no protocols at all. Load those as the startup
configs to work through the lab yourself.

## Running the lab

1. Build the topology in EVE-NG from the interface map in
   [`addressing-plan.md`](addressing-plan.md): 14 nodes, 18 links. The `.unl`
   is deliberately not published — it embeds every node's startup-config,
   including the password hashes and an OSPF key stored as Cisco type 7,
   which is reversible encryption rather than a hash.
2. Load [`configs-skeleton/`](configs-skeleton) as the startup-configs to work
   through the lab yourself, or [`configs/`](configs) for the finished state —
   in those, the `secret` and `md5` values are redacted, so substitute your own.
3. Confirm both node images are present under `/opt/unetlab/addons/qemu/`.
4. Start all nodes and give the switches about two minutes to boot.
5. Work through [`verification.md`](verification.md) in order.

If a node boots with the factory hostname (`Switch>`), its startup-config was not
applied: EVE-NG only injects it into a node that boots clean. Stop that node,
**Wipe** it, and start it again.

Full addressing and the interface-by-interface map:
[`addressing-plan.md`](addressing-plan.md).
