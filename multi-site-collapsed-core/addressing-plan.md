# IP Addressing Plan — Multi-Site Collapsed-Core Enterprise Network

Lab file: `lab01-collapsed-core-lan.unl` · 14 nodes · 18 links

All addressing below is taken from the running lab, not from an earlier draft.
Every subnet's third octet is its VLAN ID, and every site is a contiguous `/16`
so that one summary route per site is enough.

## Address blocks

| Block | Purpose |
|---|---|
| `10.0.0.0/16` | Everything in Site-DC |
| `10.1.0.0/16` | Everything in Site-A |
| `10.2.0.0/16` | Everything in Site-B |
| `10.N.0.0/30` | The routed link between a site's router and its multilayer switch |
| `10.N.<vlan>.0/24` | The site's user and service VLANs |
| `10.N.255.0/24` | Loopbacks, inside the site's own summary |
| `172.16.0.0/28` | The three WAN links of the inter-site triangle |

The site summary is what makes the plan work: a single `10.1.0.0/16` seen from
Site-DC covers Site-A's VLANs, its transit `/30` **and** its loopbacks. Routing
each remote VLAN individually — as an earlier revision did — leaves the
point-to-point links unreachable from the other sites, so inter-site
`traceroute` stops one hop short of the far switch.

## Loopbacks

| Device | Loopback0 | Role |
|---|---|---|
| RTR-DC-01 | `10.0.255.1/32` | OSPF router ID, NTP master, DHCP relay target for Site-DC |
| CSW-DC-01 | `10.0.255.2/32` | OSPF router ID |
| RTR-A-01 | `10.1.255.1/32` | OSPF router ID, DHCP relay target for Site-A |
| CSW-A-01 | `10.1.255.2/32` | OSPF router ID |
| RTR-B-01 | `10.2.255.1/32` | OSPF router ID, DHCP relay target for Site-B |
| CSW-B-01 | `10.2.255.2/32` | OSPF router ID |

Router IDs are pinned to these addresses with `router-id`. Left to itself, IOS
picks the highest interface address and the ID changes the day an interface does.

## Routed link inside each site

One `/30` per site, between the router and the multilayer switch. This is the
only OSPF adjacency in each site.

| Subnet | Router | Interface | IP | Multilayer | Interface | IP |
|---|---|---|---|---|---|---|
| `10.0.0.0/30` | RTR-DC-01 | Gi0/0 | `.1` | CSW-DC-01 | Gi0/0 | `.2` |
| `10.1.0.0/30` | RTR-A-01 | Gi0/2 | `.1` | CSW-A-01 | Gi0/0 | `.2` |
| `10.2.0.0/30` | RTR-B-01 | Gi0/2 | `.1` | CSW-B-01 | Gi0/0 | `.2` |

Both ends run `ip ospf network point-to-point` to skip the DR/BDR election, and
`ip ospf authentication message-digest` with key 1.

## WAN triangle

Three point-to-point links carved out of `172.16.0.0/28`. Every router reaches
both of the others directly, which is what makes the floating backup routes
possible.

| Subnet | Side A | Interface | IP | Side B | Interface | IP |
|---|---|---|---|---|---|---|
| `172.16.0.0/30` | RTR-DC-01 | Gi0/2 | `.1` | RTR-A-01 | Gi0/1 | `.2` |
| `172.16.0.4/30` | RTR-DC-01 | Gi0/1 | `.5` | RTR-B-01 | Gi0/0 | `.6` |
| `172.16.0.8/30` | RTR-A-01 | Gi0/0 | `.9` | RTR-B-01 | Gi0/1 | `.10` |

These links carry **no OSPF**. Inter-site reachability is static on purpose, so
the lab exercises summarisation, administrative distance and object tracking
rather than repeating what Lab 02 already does with a routing protocol.

## Inter-site static routing

Four routes per router: two primaries tied to an IP SLA probe, two floating
backups over the third side of the triangle.

| Device | Route | Purpose |
|---|---|---|
| RTR-DC-01 | `10.1.0.0/16 → 172.16.0.2 track 1` | Site-A, direct |
| RTR-DC-01 | `10.2.0.0/16 → 172.16.0.6 track 2` | Site-B, direct |
| RTR-DC-01 | `10.1.0.0/16 → 172.16.0.6 100` | Site-A via Site-B when the direct link fails |
| RTR-DC-01 | `10.2.0.0/16 → 172.16.0.2 100` | Site-B via Site-A |
| RTR-A-01 | `10.0.0.0/16 → 172.16.0.1 track 1`, `10.2.0.0/16 → 172.16.0.10 track 2`, plus the two floats | mirror image |
| RTR-B-01 | `10.0.0.0/16 → 172.16.0.5 track 1`, `10.1.0.0/16 → 172.16.0.9 track 2`, plus the two floats | mirror image |

Each multilayer switch carries a single default route toward its own site router
(`ip route 0.0.0.0 0.0.0.0 10.N.0.1`); it learns nothing else from outside its
site.

### IP SLA and object tracking

EVE-NG links are bridges, and **a bridge does not propagate link-down**: shutting
an interface at one end leaves the far end `up/up`, so the connected route
survives and an untracked static route is never withdrawn. Without this, the
failure test cannot pass.

```
ip sla 1
 icmp-echo <neighbour> source-interface <interface>
 frequency 5
ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability
ip route <summary> <mask> <neighbour> track 1
```

When the neighbour stops answering, the primary leaves the table within about ten
seconds and the floating route takes over.

## User VLANs

Gateway `.1` in every VLAN is the SVI on the site's multilayer switch. There is
no first-hop redundancy here — a collapsed core with a single multilayer switch
per site has nothing to fail over to, and pretending otherwise would be
dishonest. FHRP is what [Lab 02](../02-three-tier-architecture/README.md) is for.

| VLAN | Name | Site-DC | Site-A | Site-B | Addressed by |
|---|---|---|---|---|---|
| 10 | Management | `10.0.10.0/24` | `10.1.10.0/24` | `10.2.10.0/24` | Static, on the switches |
| 20 | Data | `10.0.20.0/24` | `10.1.20.0/24` | `10.2.20.0/24` | DHCP relay |
| 30 | Voice | `10.0.30.0/24` | `10.1.30.0/24` | `10.2.30.0/24` | DHCP relay |
| 99 | Native-Trunk | — | — | — | Not addressed |
| 100 | Server | `10.0.100.0/24` | `10.1.100.0/24` | `10.2.100.0/24` | Static |
| 199 | Isolated-Lab | `10.0.199.0/24` | `10.1.199.0/24` | `10.2.199.0/24` | Static |
| 1000 | Unused-Parking | — | — | — | Not addressed |

### Switch management addresses

| Device | VLAN 10 address |
|---|---|
| ASW-DC-01 | `10.0.10.11` |
| ASW-DC-02 | `10.0.10.12` |
| ASW-A-01 | `10.1.10.11` |
| ASW-B-01 | `10.2.10.11` |

Each access switch also carries `ip default-gateway 10.N.10.1`, since they run
`no ip routing`. Without both of these an access switch has SSH configured and
is still unreachable.

### Endpoints

| Endpoint | VLAN | Address | Notes |
|---|---|---|---|
| SRV-DC-01 | 199 | `10.0.199.10/24` | Static |
| SRV-DC-02 | 20 | `10.0.20.100/24` | **DHCP client** — proves the relay works |
| SRV-A-01 | 199 | `10.1.199.10/24` | Static |
| SRV-B-01 | 199 | `10.2.199.10/24` | Static |

The DHCP pools exclude `.1`–`.99`, and the skeleton config gives SRV-DC-02 the
static address `10.0.20.50` inside that excluded range. So an address of
`10.0.20.100` can only have come from the relay, never from the skeleton.

### DHCP pools

Both user VLANs of each site are served by that site's router, reached through
`ip helper-address 10.N.255.1` on the SVI.

```
ip dhcp excluded-address 10.0.20.1 10.0.20.99
ip dhcp pool SITE-DC-VLAN20
 network 10.0.20.0 255.255.255.0
 default-router 10.0.20.1
 domain-name lab.example
 lease 0 8
```

The VLAN 30 pool adds `option 150 ip 10.N.100.10` for phone provisioning.

## Access-layer EtherChannel

Every access switch reaches its multilayer switch over a two-link bundle. The
bundles are **static** (`mode on`) — see the platform note in
[`README.md`](README.md).

| Bundle | Multilayer side | Access side |
|---|---|---|
| CSW-DC-01 Po1 | Gi0/1 + Gi1/0 | ASW-DC-01 Gi0/0 + Gi1/0 (Po1) |
| CSW-DC-01 Po2 | Gi0/2 + Gi1/1 | ASW-DC-02 Gi0/0 + Gi1/0 (Po1) |
| CSW-A-01 Po1 | Gi0/1 + Gi1/0 | ASW-A-01 Gi0/0 + Gi1/0 (Po1) |
| CSW-B-01 Po1 | Gi0/1 + Gi1/0 | ASW-B-01 Gi0/0 + Gi1/0 (Po1) |

All bundles are 802.1Q trunks with native VLAN 99, allowing `10,20,30,99,100,199`.
Every member of a bundle must carry **identical** switchport configuration; a
single mismatched `switchport nonegotiate` is enough to leave the second member
suspended.

## Interface map

| Device | Gi0/0 | Gi0/1 | Gi0/2 | Gi0/3 | Gi1/0 | Gi1/1 | Gi1/2 | Gi1/3 |
|---|---|---|---|---|---|---|---|---|
| RTR-DC-01 | CSW-DC-01 | RTR-B-01 | RTR-A-01 | — | | | | |
| RTR-A-01 | RTR-B-01 | RTR-DC-01 | CSW-A-01 | — | | | | |
| RTR-B-01 | RTR-DC-01 | RTR-A-01 | CSW-B-01 | — | | | | |
| CSW-DC-01 | RTR-DC-01 | ASW-DC-01 | ASW-DC-02 | — | ASW-DC-01 | ASW-DC-02 | — | — |
| CSW-A-01 | RTR-A-01 | ASW-A-01 | — | — | ASW-A-01 | — | — | — |
| CSW-B-01 | RTR-B-01 | ASW-B-01 | — | — | ASW-B-01 | — | — | — |
| ASW-DC-01 | CSW-DC-01 | SRV-DC-01 | — | — | CSW-DC-01 | — | — | — |
| ASW-DC-02 | CSW-DC-01 | SRV-DC-02 | — | — | CSW-DC-01 | — | — | — |
| ASW-A-01 | CSW-A-01 | SRV-A-01 | — | — | CSW-A-01 | — | — | — |
| ASW-B-01 | CSW-B-01 | SRV-B-01 | — | — | CSW-B-01 | — | — | — |

Every **switch** interface shown as `—` is shut, described `UNUSED - parked`
and parked in VLAN 1000. On the routers, `Gi0/3` is `description UNUSED`,
`no ip address`, `shutdown`: a routed port cannot be put in a VLAN.

## Console ports

EVE-NG assigns them in node order starting at 32769:

```
RTR-DC-01 32769   RTR-A-01  32770   RTR-B-01  32771   CSW-DC-01 32772
CSW-A-01  32773   CSW-B-01  32774   ASW-DC-01 32775   ASW-DC-02 32776
ASW-A-01  32777   ASW-B-01  32778   SRV-DC-01 32779   SRV-DC-02 32780
SRV-A-01  32781   SRV-B-01  32782
```

`telnet <eve-ip> <port>` is usually quicker than the HTML5 console.

## Platform note

`RTR-*` are **IOSv (`vios`) routers** with four interfaces; their ports are
routed already, so `no switchport` is invalid on them. `CSW-*` and `ASW-*` are
**IOSvL2 (`viosl2`)** with eight interfaces, where `no switchport` is required to
turn a port into a routed interface — used on `Gi0/0` of each multilayer switch
and nowhere else.
