# IP Addressing Plan — ASA Destination NAT and ACL

10 nodes · 9 links · 6 GB of RAM
(4 × 1024 MB for the IOSv/IOSvL2 nodes, 2048 MB for the ASAv; the five VPCS
endpoints cost essentially nothing).

All addressing below is taken from the rebuilt lab and from the saved
verification run, not from the earlier revision published on GitHub. Everything
that represents the public Internet uses documentation-only ranges (RFC 5737),
so the lab is portable and never collides with a real network. The previous
revision advertised `8.8.8.8` as the virtual address and `4.4.4.0/29` as the ISP
segment; both are real, routable addresses and both are gone.

The whole lab exists to make one sentence true: **an external client always
reaches Server-A at `198.51.100.8`, and that stays true when the server moves to
the other site.** Read the plan with that in mind — the interesting column is
not "which address", it is "what has to change when the server moves". In the
firewall the answer is one line. The server itself becomes a host of the other
site's VLAN, and nothing else in the lab moves at all.

## Address blocks

| Block | Purpose |
|---|---|
| `203.0.113.0/30` | Outside link: R-Client `Gi0/0` ↔ ASA `Gi0/0` |
| `203.0.113.32/27` | External client LAN behind R-Client — the source object of the NAT rule |
| `192.0.2.0/30` | ASA inside ↔ SW-A: the only link the firewall speaks OSPF on |
| `192.0.2.4/30` | Site-A ↔ Site-B transit, SW-A ↔ SW-B |
| `192.0.2.8/30` | Site-B ↔ ISP transit, SW-B ↔ R-ISP |
| `198.51.100.0/29` | ISP segment: R-ISP `Gi0/0` and the ISP's own server |
| `192.168.1.0/24` | Site-A, VLAN 10 |
| `10.100.100.0/24` | Site-B, VLAN 10 |
| `10.255.0.0/24` | Loopbacks and OSPF router IDs — never carries user traffic |
| `198.51.100.8/32` | The published virtual address. **No interface anywhere carries it.** |

The two `203.0.113.x` blocks do not overlap: the outside `/30` covers `.0`–`.3`
and the client LAN covers `.32`–`.63`. They are drawn from the same
documentation `/24` on purpose, because from the firewall's point of view both
are "outside" and it reads better in `show route`.

## The virtual address belongs to no subnet

`198.51.100.8` is the address the client is told to use, and no device in the
lab owns it. The ASA's router ID `10.255.0.254` is unowned too, but nothing ever
sends a packet to it; this one takes real traffic.

It sits one past the top of the ISP segment: `198.51.100.0/29` covers `.0`
through `.7`, so `.8` is outside it. That near-miss is deliberate. It looks like
it ought to live on the ISP's wire, and it does not live anywhere — it exists
only as an object on the ASA:

```
object network VIP_SERVER_A
 host 198.51.100.8
 description Fixed virtual address published to external clients
```

No interface is numbered with it, no OSPF process advertises it, and no host
answers to it. PC-Ext can reach it only because R-Client has a default route
toward the firewall (`ip route 0.0.0.0 0.0.0.0 203.0.113.2`) and the ASA
rewrites the destination before the packet is routed any further. `show nat
detail` says it in one line: the destination origin is always `198.51.100.8/32`
and the translation is whatever `SERVER_A` currently holds — `10.100.100.10/32`
while the server is in Site-B. The captured output is under "What changes when
the server moves", below.

That is the lesson of the lab. A published address does not have to be an
address that exists; it has to be an address the firewall knows how to rewrite.

## Point-to-point and transit links

Every device-to-device link outside the two site VLANs is a routed `/30`; the
only other segments are the client LAN (`/27`) and the ISP LAN (`/29`). The path from the
external client to the ISP is a straight line — there is no redundancy in this
lab and none is implied.

| Subnet | Device A | Interface | IP | Device B | Interface | IP |
|---|---|---|---|---|---|---|
| `203.0.113.32/27` | R-Client | Gi0/1 | `.33` | PC-Ext | eth0 | `.34` |
| `203.0.113.0/30` | R-Client | Gi0/0 | `.1` | ASA (outside) | Gi0/0 | `.2` |
| `192.0.2.0/30` | ASA (inside) | Gi0/1 | `.1` | SW-A | Gi0/3 | `.2` |
| `192.0.2.4/30` | SW-A | Gi0/2 | `.5` | SW-B | Gi0/2 | `.6` |
| `192.0.2.8/30` | SW-B | Gi0/3 | `.9` | R-ISP | Gi0/1 | `.10` |
| `198.51.100.0/29` | R-ISP | Gi0/0 | `.1` | SRV-ISP | eth0 | `.4` |

The client LAN is a `/27` rather than a `/32` host route. In the published
revision the NAT source object was a single host, so there was no client
network to speak of. A real `/27` makes `nat ... source dynamic CLIENT_LAN
interface` mean what it says, and makes the return route on the firewall a
real prefix —
`route outside 203.0.113.32 255.255.255.224 203.0.113.1 1`.

## Site VLANs

One VLAN per site, same ID on both, different subnets. The gateway is the SVI on
that site's multilayer switch; there is no first-hop redundancy here, and
pretending otherwise would be dishonest — Lab 02 is where FHRP lives.

| Site | VLAN | Name | Subnet | Gateway | Gateway lives on | OSPF |
|---|---|---|---|---|---|---|
| Site-A | 10 | `Site-A_Users` | `192.168.1.0/24` | `192.168.1.1` | SW-A `Vlan10` | area 0, passive |
| Site-B | 10 | `Site-B_Users` | `10.100.100.0/24` | `10.100.100.1` | SW-B `Vlan10` | area 0, passive |

Both SVIs are `passive-interface`: the prefix is advertised, but no adjacency is
attempted toward the hosts.

## Endpoints

| Endpoint | Site / segment | Address | Gateway | Connected to |
|---|---|---|---|---|
| PC-Ext | Client LAN | `203.0.113.34/27` | `203.0.113.33` | R-Client Gi0/1 |
| PC-A | Site-A, VLAN 10 | `192.168.1.11/24` | `192.168.1.1` | SW-A Gi0/1 |
| Server-B | Site-B, VLAN 10 | `10.100.100.11/24` | `10.100.100.1` | SW-B Gi0/1 |
| SRV-ISP | ISP segment | `198.51.100.4/29` | `198.51.100.1` | R-ISP Gi0/0 |
| **Server-A** | **Site-B, VLAN 10 (current)** | **`10.100.100.10/24`** | `10.100.100.1` | **SW-B Gi0/0 — its only cable** |

Server-A appears once, because there is one of it. The published revision listed
it in both sites, which quietly turned a site migration into a `shutdown`
exercise and taught the wrong thing.

### Server-A has one cable

A server is not in two cities at once, so it is not wired to two sites. Server-A
is a VPCS with a single `eth0`, plugged into whichever site it currently lives
in. **Right now that is Site-B.** The other site keeps an access port waiting for
it: same VLAN, never shut, fully configured, and with nothing plugged into it —
so it is `down/down` until the server arrives, which is exactly right.

| Site | Port | State | Description in the config |
|---|---|---|---|
| Site-B | SW-B `Gi0/0` | Cabled — Server-A is here | `To Server-A eth0` |
| Site-A | SW-A `Gi0/0` | Reserved, no cable | `Reserved for Server-A - no cable, server is in Site-B` |

The reserved port is a normal VLAN 10 access port with `spanning-tree portfast
edge`, not a shut port. The verification reads all three facts off the running
configs separately — SW-B `Gi0/0` described toward Server-A, SW-A `Gi0/0`
described as reserved and uncabled, and SW-A `Gi0/0` still carrying
`switchport access vlan 10` — so the reservation cannot rot unnoticed.

Moving the server means moving the cable: out of SW-B `Gi0/0`, into SW-A
`Gi0/0`. It is a real recable, not a `shutdown`, and it is done by hand on the
EVE-NG canvas, with the three nodes the cable touches stopped first: Server-A,
SW-B and SW-A. The REST API can do it too, with two catches: the new
network must be created with `visibility: 1` — with `0` the interface `PUT`s
answer `fail` — and the `POST` and the two `PUT`s must not yield between them,
or EVE-NG purges the network for having no endpoints.

Either way the cable really moves, and that is the right price for representing
the scenario honestly.

### The two addresses Server-A can have

| Site | Address | Gateway | Reached from outside as |
|---|---|---|---|
| Site-A | `192.168.1.10/24` | `192.168.1.1` | `198.51.100.8` |
| Site-B | `10.100.100.10/24` | `10.100.100.1` | `198.51.100.8` |

Both rows are the same lab. Only one is true at a time, and the right-hand
column never changes — that is the entire point.

## Loopbacks and OSPF router IDs

| Device | Loopback0 | Router ID | Notes |
|---|---|---|---|
| SW-A | `10.255.0.1/32` | `10.255.0.1` | In area 0 |
| SW-B | `10.255.0.2/32` | `10.255.0.2` | In area 0 |
| R-ISP | `10.255.0.3/32` | `10.255.0.3` | In area 0 |
| ASA | — | `10.255.0.254` | Identifier only: no interface carries it |
| R-Client | — | — | Speaks no OSPF at all |

The ASA's router ID is a name, not an address. It is set with `router-id
10.255.0.254` under `router ospf 1`, no interface is numbered with it, and the
firewall's only `network` statement is `192.0.2.0 255.255.255.252 area 0`, so it
is never advertised. Router IDs are pinned everywhere for the usual reason: left
alone, the device picks the highest interface address and the ID changes the day
an interface does.

R-Client having no router ID is a design decision, not an omission. In the
published revision OSPF crossed the firewall and handed the external client the
whole internal topology. Now the firewall speaks OSPF on `inside` only, with MD5
authentication, and R-Client keeps a single default route. The verification
confirms both halves: R-Client has no OSPF neighbour, and R-Client learns no
internal prefix.

## The ASA's objects

Three objects carry the whole design. Every address the NAT rule and the ACL
care about is reached through one of them, which is why the migration touches
one line.

| Object | Type | Value now | What it means |
|---|---|---|---|
| `SERVER_A` | host | `10.100.100.10` | Server-A's **real** address, in whichever site it currently lives. The only line that changes when the server moves. |
| `CLIENT_LAN` | subnet | `203.0.113.32 255.255.255.224` | The external client LAN behind R-Client. Source of the NAT rule, source of every ACE. |
| `VIP_SERVER_A` | host | `198.51.100.8` | The fixed virtual address published to clients. Belongs to no subnet in the lab. |

They are used in exactly two constructs — one NAT rule and one ACL:

```
nat (outside,inside) source dynamic CLIENT_LAN interface destination static VIP_SERVER_A SERVER_A
access-list OUTSIDE_IN extended permit icmp object CLIENT_LAN object SERVER_A echo
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq ssh
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq https
access-list OUTSIDE_IN extended permit udp object CLIENT_LAN object SERVER_A range 33434 33463
```

Two of those ACEs carry a caveat, spelled out in full under "Addresses the
outside world can see": Server-A is a VPCS and answers neither SSH nor HTTPS, so
those two lines prove the firewall permits and translates the flow and nothing
more; and the UDP range is a deliberate exception to the policy, added so the
traceroute section works.

Two things about those five lines matter for addressing.

**The NAT rule ends at `SERVER_A`, not at the mapped object.** In the published
revision it stopped after the mapped object; the ASA rejects that with
`Incomplete command`, and `SERVER_A` was left defined and unused. The rule only
becomes a destination NAT when it ends `destination static VIP_SERVER_A
SERVER_A`.

**The ACL is written against the real address, not the virtual one.** Since ASA
8.3 an interface ACL is evaluated *after* the destination has been untranslated,
so `permit tcp any host 198.51.100.8` never matches anything. Using the object
fixes that and, as a side effect, makes the lab's promise true — the ACL follows
the server automatically. You can see the object expand:

```
access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 10.100.100.10 echo (hitcnt=7)
```

and after the migration, with nothing in the ACL edited, the same line reads
`host 192.168.1.10`.

## What changes when the server moves

| Thing | Changes? |
|---|---|
| Server-A's cable | Yes — unplug from SW-B `Gi0/0`, plug into SW-A `Gi0/0` |
| Server-A's own address and gateway | Yes — it is now a host of the other site's VLAN 10 |
| `object network SERVER_A` → `host …` | Yes — one line |
| The `nat` rule | No |
| The `OUTSIDE_IN` ACL | No |
| The client's configuration | No |
| `198.51.100.8` | No |

The evidence is a before/after pair taken from the running lab. With Server-A in
Site-B, `show xlate` reads `NAT from inside:10.100.100.10 to
outside:198.51.100.8`; after the migration to Site-A the same command reads
`NAT from inside:192.168.1.10 to outside:198.51.100.8`, and `show nat detail`
shows the same rule with only the destination translation different:

```
Manual NAT Policies (Section 1)
1 (outside) to (inside) source dynamic CLIENT_LAN interface  destination static VIP_SERVER_A SERVER_A
    translate_hits = 21, untranslate_hits = 30
    Source - Origin: 203.0.113.32/27, Translated: 192.0.2.1/30
    Destination - Origin: 198.51.100.8/32, Translated: 192.168.1.10/32
```

PC-Ext's ping to `198.51.100.8` succeeds 4/4 both times. The only thing that
changes in the ping is the TTL — 60 from Site-B, 61 from Site-A — because Site-A
is one hop closer to the firewall. The traceroute changes too, by one hop; that
is in the next section.

## Addresses the outside world can see

Three points here are worth stating plainly rather than hiding.

**Server-A is a VPCS. It does not serve SSH or HTTPS.** The `eq ssh` and
`eq https` ACEs demonstrate that the firewall *permits and translates* those
flows all the way to the real address — `packet-tracer` returns `Action: allow`,
the ACEs expand to `host 10.100.100.10` and accumulate hits, and `show nat
detail` carries the destination translation itself. Whether a service answers on the far end is out of scope for this lab, and
the verification does not claim otherwise.

**The UDP range `33434`–`33463` is a deliberate exception.** The stated policy
of `OUTSIDE_IN` is ICMP echo, SSH and HTTPS only. That fourth ACE exists so the
traceroute section of the lab works, and it is documented as an exception rather
than smuggled in as if it belonged.

**Turning on `inspect icmp error` exposes internal addresses.** It is what makes
traceroute return hops instead of stars, together with `inspect icmp` and
`set connection decrement-ttl` on `class-default`. The price is that the
external client sees transit addresses it would not otherwise see. With
Server-A in Site-B, a trace run from R-Client sourced on its client-LAN
interface (`203.0.113.33`) returns these four hops:

```
203.0.113.2   192.0.2.2   192.0.2.6   198.51.100.8
```

`192.0.2.2` is SW-A and `192.0.2.6` is SW-B. After the migration to Site-A the
trace is one hop shorter — `203.0.113.2`, `192.0.2.2`, `198.51.100.8` — because
SW-B is no longer on the path. In both cases the final hop is reported as
`198.51.100.8`: the real address of the server never appears outside the
firewall.

## Interface map

| Device | Gi0/0 | Gi0/1 | Gi0/2 | Gi0/3 | Gi1/0 | Gi1/1 | Gi1/2 | Gi1/3 |
|---|---|---|---|---|---|---|---|---|
| R-Client | ASA (outside) | PC-Ext | — | — | | | | |
| ASA | R-Client (`outside`) | SW-A (`inside`) | — | — | | | | |
| SW-A | *reserved for Server-A* | PC-A | SW-B | ASA | — | — | — | — |
| SW-B | Server-A | Server-B | SW-A | R-ISP | — | — | — | — |
| R-ISP | SRV-ISP | SW-B | — | — | | | | |

On the IOSv and IOSvL2 nodes, interfaces shown as `—` are `shutdown` and
described `UNUSED`. The ASA is the exception twice over: it has seven data ports
rather than the eight columns above, and its spare ports carry no description at
all — `Gi0/2` through `Gi0/6` and `Management0/0` are simply shut, with
`no nameif`, `no security-level` and `no ip address`. This lab uses no
management interface.

On the switches only `Gi0/2` and `Gi0/3` are routed (`no switchport`); `Gi0/0`
and `Gi0/1` are VLAN 10 access ports.

## Console ports

EVE-NG assigns `32768 + node id`, so:

```
PC-Ext   32769   R-Client 32770   ASA      32771   SW-A     32772
SW-B     32773   R-ISP    32774   SRV-ISP  32775   PC-A     32776
Server-A 32777   Server-B 32778
```

`telnet <eve-ip> <port>` is usually quicker than the HTML5 console.

## Platform notes

**`R-Client` and `R-ISP` are IOSv (`vios`) routers** with four interfaces. Their
ports are routed already, so `no switchport` is invalid on them.
**`SW-A` and `SW-B` are IOSvL2 (`viosl2`)** with eight, where `no switchport` is
required to turn a port into a routed interface — used on `Gi0/2` and `Gi0/3`
and nowhere else.

**The ASAv's interface indices are offset by one.** Index 0 is `Management0/0`,
not `GigabitEthernet0/0`. Copying an IOSv mapping shifts the firewall's entire
cabling by one position, and the symptom is an ASA that boots perfectly and sees
nobody. `Gi0/0` is `outside`, `Gi0/1` is `inside`.

**The ASAv needs `console serial`.** Without it the appliance boots fine and its
serial console stays silent forever, which in EVE-NG looks exactly like a dead
node. It is in the skeleton config for that reason, and it is kept in the
published config on purpose.

**The SVI needs to be recreated by hand.** An SVI that comes from the
startup-config EVE-NG injects stays `down/down` even with the VLAN active and
its access ports forwarding; neither `no shutdown` nor bouncing a port fixes it.
`no interface Vlan10` followed by re-entering it does. The tell is the `Method`
column of `show ip interface brief`: `TFTP` while it is broken, `manual` once
it has been rebuilt.

## Verification

The rebuilt lab passes 45 automated checks with zero failures, covering
addressing, the single-cable rule and its reserved port, OSPF containment,
NAT translation, ACL evaluation against the real address, denied traffic, and
traceroute. See `verification.md`.
