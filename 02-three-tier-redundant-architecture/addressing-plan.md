# IP Addressing Plan — Three-Tier Architecture with L3 Redundancy

18 nodes · 26 links · 4 user VLANs

All addressing below is taken from the running lab topology, not from an earlier
draft. Documentation-only ranges (RFC 5737) are used for anything representing
the public Internet, so the lab is portable and never collides with a real
network.

## Address blocks

| Block | Purpose |
|---|---|
| `10.222.0.0/24` | Loopback0 on every internal device — stable OSPF router IDs |
| `10.0.0.0/24` | Layer 3 transit links, carved into `/30` point-to-point subnets |
| `10.10.10.0/24` – `10.10.40.0/24` | Four user VLANs |
| `192.0.2.0/30`, `198.51.100.0/30` | Core-to-ISP edge links (RFC 5737) |
| `203.0.113.0/24` | Simulated Internet: the two ISP loopbacks (`.1`, `.2`) and the ISP-to-ISP peering link (`.4/30`) |

## Loopbacks

| Device | Loopback0 | Role |
|---|---|---|
| C-SW-1 | `10.222.0.1/32` | Core, OSPF router ID |
| C-SW-2 | `10.222.0.2/32` | Core, OSPF router ID |
| D-SW-1 | `10.222.0.3/32` | Distribution, OSPF router ID |
| D-SW-2 | `10.222.0.4/32` | Distribution, OSPF router ID |
| ISP-1 | `203.0.113.1/32` | Simulated Internet destination |
| ISP-2 | `203.0.113.2/32` | Simulated Internet destination |

## Layer 3 transit links

Every Core–Distribution pair is a routed `/30`. Each Distribution switch reaches
**both** Core devices, so losing one Core or one link never isolates a floor.

| Subnet | Device A | Interface | IP | Device B | Interface | IP |
|---|---|---|---|---|---|---|
| `10.0.0.0/30` | C-SW-1 | Gi0/1 | `.1` | D-SW-1 | Gi0/2 | `.2` |
| `10.0.0.4/30` | C-SW-1 | Gi0/2 | `.5` | D-SW-2 | Gi0/3 | `.6` |
| `10.0.0.8/30` | C-SW-2 | Gi0/2 | `.9` | D-SW-1 | Gi0/3 | `.10` |
| `10.0.0.12/30` | C-SW-2 | Gi0/1 | `.13` | D-SW-2 | Gi0/2 | `.14` |
| `10.0.0.20/30` | C-SW-1 | Gi0/3 | `.21` | C-SW-2 | Gi0/3 | `.22` |

`10.0.0.16/30` is deliberately left unused: it belonged to the Distribution–
Distribution routed link of an earlier revision, which is now a Layer 2
EtherChannel instead. It is reserved rather than reassigned so that older
diagrams remain unambiguous.

## Internet edge

Each Core device faces its own ISP router. There is no shared Internet segment
and no HSRP at the edge — redundancy comes from two independent upstreams, the
Core–Core link, and a peering link between the two ISPs.

| Subnet | Side A | Interface | IP | Side B | Interface | IP |
|---|---|---|---|---|---|---|
| `192.0.2.0/30` | ISP-1 | Gi0/0 | `.2` | C-SW-1 | Gi0/0 | `.1` |
| `198.51.100.0/30` | ISP-2 | Gi0/0 | `.2` | C-SW-2 | Gi0/0 | `.1` |
| `203.0.113.4/30` | ISP-1 | Gi0/1 | `.5` | ISP-2 | Gi0/1 | `.6` |

The peering `/30` sits inside `203.0.113.0/24` without colliding with the two
`/32` loopbacks (`.1` and `.2`), because it covers `.4`–`.7`.

### Why the peering link exists

Both Core devices originate a default route, so campus traffic toward the
Internet is load-shared across the two upstreams. Without a link between the
ISPs each one knows only its own loopback, and roughly half the traffic to
`203.0.113.1` / `203.0.113.2` died at whichever ISP the hash happened to pick.
One peering link and one static route per side fixes that, and it doubles as the
recovery path when an upstream fails.

### Static routing at the edge

| Device | Route | Purpose |
|---|---|---|
| C-SW-1 | `0.0.0.0/0 → 192.0.2.2 track 1` | Default out; withdrawn when ISP-1 stops answering |
| C-SW-2 | `0.0.0.0/0 → 198.51.100.2 track 1` | The same, toward ISP-2 |
| ISP-1 | `10.0.0.0/8 → 192.0.2.1 track 1` | Return path to the campus |
| ISP-1 | `10.0.0.0/8 → 203.0.113.6 200` | Floating backup return, over the peering link |
| ISP-1 | `203.0.113.2/32 → 203.0.113.6` | Reach the other ISP's loopback |
| ISP-2 | mirror image of the three above | |

Reachability to **both** `203.0.113.1` and `203.0.113.2` is what proves Internet
access works. Testing only one of them hides half the failure modes.

### IP SLA and object tracking

EVE-NG links are bridges, and **a bridge does not propagate link-down**: shutting
an interface at one end leaves the far end `up/up`. Without tracking, a Core goes
on advertising a default route toward an ISP that is gone and the traffic
disappears into a black hole — the failure test looks like a design bug when it
is really a simulator artefact.

So each edge device pings its neighbour every 5 seconds and ties its static route
to the result:

```
ip sla 1
 icmp-echo <neighbour> source-interface GigabitEthernet0/0
 frequency 5
ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability
ip route <prefix> <neighbour> track 1
```

When the neighbour stops answering the route leaves the table; on a Core that
also stops the OSPF default advertisement, so the whole campus shifts to the
other upstream by itself.

## User VLANs

Gateway `.1` in every VLAN is an HSRP virtual IP. The active router alternates
per VLAN so both Distribution switches carry traffic in steady state, and either
one can carry all of it during a failure.

| VLAN | Subnet | Gateway (HSRP VIP) | D-SW-1 SVI | D-SW-2 SVI | Active | Access switch | Hosts |
|---|---|---|---|---|---|---|---|
| 10 | `10.10.10.0/24` | `.1` | `.2` | `.3` | D-SW-1 | A-SW-1 | PC-1 `.100`, PC-2 `.101` |
| 20 | `10.10.20.0/24` | `.1` | `.3` | `.2` | D-SW-2 | A-SW-2 | PC-3 `.100`, PC-4 `.101` |
| 30 | `10.10.30.0/24` | `.1` | `.2` | `.3` | D-SW-1 | A-SW-3 | PC-5 `.100`, PC-6 `.101` |
| 40 | `10.10.40.0/24` | `.1` | `.3` | `.2` | D-SW-2 | A-SW-4 | PC-7 `.100`, PC-8 `.101` |

The switch holding the lower SVI octet (`.2`) is the intended HSRP active for
that VLAN; align HSRP priority with that column and enable preemption so the
assignment survives a reload.

### Access switch management addresses

Each access switch has one SVI in the VLAN it serves, with the HSRP VIP as its
default gateway. They exist so the switches can be reached and can `ping` their
own gateway; they take no part in routing.

| Switch | SVI | Address | Default gateway |
|---|---|---|---|
| A-SW-1 | Vlan10 | `10.10.10.10/24` | `10.10.10.1` |
| A-SW-2 | Vlan20 | `10.10.20.10/24` | `10.10.20.1` |
| A-SW-3 | Vlan30 | `10.10.30.10/24` | `10.10.30.1` |
| A-SW-4 | Vlan40 | `10.10.40.10/24` | `10.10.40.1` |

So inside each user `/24`: `.1` is the VIP, `.2`/`.3` the two Distribution SVIs,
`.10` the access switch, and `.100`/`.101` the hosts.

## Distribution interconnect

`Po1` bundles `Gi0/0` and `Gi0/1` between D-SW-1 and D-SW-2 using LACP. It is a
**pure Layer 2** trunk: no IP address and no OSPF adjacency across it. It exists
so both Distribution switches see every user VLAN, which is what makes HSRP
possible in the first place.

## Interface map

| Device | Gi0/0 | Gi0/1 | Gi0/2 | Gi0/3 | Gi1/0 | Gi1/1 | Gi1/2 | Gi1/3 |
|---|---|---|---|---|---|---|---|---|
| ISP-1 | C-SW-1 | ISP-2 | — | — | | | | |
| ISP-2 | C-SW-2 | ISP-1 | — | — | | | | |
| C-SW-1 | ISP-1 | D-SW-1 | D-SW-2 | C-SW-2 | | | | |
| C-SW-2 | ISP-2 | D-SW-2 | D-SW-1 | C-SW-1 | | | | |
| D-SW-1 | Po1 | Po1 | C-SW-1 | C-SW-2 | A-SW-1 | A-SW-2 | A-SW-3 | A-SW-4 |
| D-SW-2 | Po1 | Po1 | C-SW-2 | C-SW-1 | A-SW-1 | A-SW-2 | A-SW-3 | A-SW-4 |
| A-SW-1 | D-SW-1 | D-SW-2 | PC-1 | PC-2 | | | | |
| A-SW-2 | D-SW-1 | D-SW-2 | PC-3 | PC-4 | | | | |
| A-SW-3 | D-SW-1 | D-SW-2 | PC-5 | PC-6 | | | | |
| A-SW-4 | D-SW-1 | D-SW-2 | PC-7 | PC-8 | | | | |

Note the deliberate asymmetry on the Distribution switches: `Gi0/2` on D-SW-1
goes to C-SW-1 while `Gi0/2` on D-SW-2 goes to C-SW-2. Each switch reaches its
"own side" Core on the lower-numbered interface.

## Platform note

`ISP-1`, `ISP-2`, `C-SW-1` and `C-SW-2` run **IOSv (`vios`) routers**, not Layer 3
switches. Their interfaces are routed by default, so `no switchport` is invalid
on them and will be rejected line by line. Only `D-SW-*` and `A-SW-*` run
IOSvL2 (`viosl2`), where `no switchport` is required to turn a port into a
routed interface.
