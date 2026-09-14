# Lab 03 — ASA Destination NAT and ACL

An external client always reaches Server-A at one fixed address, `198.51.100.8`.
That address belongs to no subnet in this lab: it exists only as a translation on
the firewall. The real server lives in Site-A (`192.168.1.10`) or in Site-B
(`10.100.100.10`), and when it moves between them **one line changes on the ASA**
— the host inside the `SERVER_A` object. The client is never told, and the ACL is
not touched.

- **Lab file:** not distributed — see *Running the lab*
- **Platform:** EVE-NG Community
- **Images:** `vios-adventerprisek9` (routers), `viosl2-adventerprisek9` (switches), `asav-992` — ASA 9.9(2)32 (firewall), VPCS (endpoints)
- **Size:** 10 nodes, 9 links, 5 QEMU nodes, 6 GB of RAM

## Topology

![Topology](topology.png)

Full addressing and the interface-by-interface map:
[`addressing-plan.md`](addressing-plan.md).
Test procedure and expected output: [`verification.md`](verification.md).

## Server-A has one cable

This is the centre of the lab and it is not softened anywhere: **a server is not
in two cities at once.** Server-A is plugged into the site it lives in, and
nowhere else. The other site keeps its access port configured, in VLAN 10, never
shut down and empty, with a description that says what it is waiting for:

```
interface GigabitEthernet0/0
 description Reserved for Server-A - no cable, server is in Site-B
 switchport access vlan 10
 switchport mode access
 spanning-tree portfast edge
```

Cabling the server to both sites and shutting one leg would turn the move into a
`shutdown`, which is a different exercise and teaches something else. Moving it
here means moving the cable.

**As shipped, Server-A is in Site-B at `10.100.100.10`**, on `SW-B Gi0/0`. The
reserved, cable-less port is `SW-A Gi0/0`.

## How the translation works

Three objects and one rule. The objects are what the rest of the configuration
refers to, so that the real address appears in exactly one place:

```
object network SERVER_A
 host 10.100.100.10
 description Server-A real address - currently in Site-B
object network CLIENT_LAN
 subnet 203.0.113.32 255.255.255.224
 description External client LAN behind R-Client
object network VIP_SERVER_A
 host 198.51.100.8
 description Fixed virtual address published to external clients

nat (outside,inside) source dynamic CLIENT_LAN interface destination static VIP_SERVER_A SERVER_A
```

One twice-NAT rule does both halves at once. A packet arriving on `outside` for
`198.51.100.8` has its **destination** rewritten to whatever `SERVER_A` currently
is; at the same time its **source** is PAT'd behind the inside interface
(`192.0.2.1`), so the server answers the firewall rather than the client. That
half is not decoration: nothing inside this lab has a route to
`203.0.113.32/27` — the ASA does not advertise it into OSPF, and SW-B's stray
default route is gone (item 7 of "What was wrong in the published version") — so
a reply addressed straight to the client would die inside. `show nat detail`
shows both halves, here with the server in Site-A:

```
1 (outside) to (inside) source dynamic CLIENT_LAN interface  destination static VIP_SERVER_A SERVER_A
    translate_hits = 21, untranslate_hits = 30
    Source - Origin: 203.0.113.32/27, Translated: 192.0.2.1/30
    Destination - Origin: 198.51.100.8/32, Translated: 192.168.1.10/32
```

The return route for the client LAN is static (`route outside 203.0.113.32
255.255.255.224 203.0.113.1 1`), because the firewall deliberately does not peer
with anything on the outside — see the OSPF note below.

## Moving Server-A between sites

Three things change, and only three.

1. **The cable.** Stop the three nodes the cable touches — Server-A, SW-B and
   SW-A — then unplug the server from `SW-B Gi0/0` and plug it into
   `SW-A Gi0/0`. Then the two descriptions swap: the port that now has the server
   says `To Server-A eth0`, and the one that lost it says
   `Reserved for Server-A - no cable, server is in Site-A`.
2. **The server's own address.** It moved to a different subnet, so it has to:
   `10.100.100.10/24` with gateway `10.100.100.1` becomes `192.168.1.10/24` with
   gateway `192.168.1.1`. That is inherent to changing site, not a cost of this
   design.
3. **One line on the ASA**, plus a `clear xlate` so the translation already in
   place is rebuilt. The object's `description` follows as bookkeeping; the
   `host` line is the change:

```
object network SERVER_A
 host 192.168.1.10
```

What does **not** change:

- **The external client.** PC-Ext keeps sending to the same address, before and
  after, with no reconfiguration of any kind:

```
before (Site-B)   84 bytes from 198.51.100.8 icmp_seq=1 ttl=60 time=2.590 ms
after  (Site-A)   84 bytes from 198.51.100.8 icmp_seq=1 ttl=61 time=2.647 ms
```

  The TTL differs by one because Site-A is one hop closer; the address does not.

- **The ACL.** Not one character of it. It is written against the `SERVER_A`
  object, so the ASA re-expands it by itself:

```
before  access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 10.100.100.10 echo (hitcnt=7)
after   access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 192.168.1.10 echo (hitcnt=4)
```

Both captures come from an actual move of the server, taken before and after;
they are reproduced in [`verification.md`](verification.md).

As shipped, the cable is in Site-B. Re-cabling a running lab
means stopping the three nodes the cable touches (Server-A and both switches)
first — EVE-NG will not re-cable a node that is running — then deleting the old
link and drawing the new one, either on the canvas or through the API. Through
the API there are two catches: the new network has to be created with
`visibility: 1`, because with `0` the interface `PUT`s come back `fail`, and the
`POST` and the two `PUT`s must not yield between them, or EVE-NG purges the
network for having no endpoints.

Needing a real cable move is the right price for representing the scenario
honestly. A server that stays plugged into both sites is not a server that
moves.

## Security policy

The `outside` interface carries a single ACL. Every ACE is written between the
client-LAN object and the server object — no literal addresses:

```
access-list OUTSIDE_IN extended permit icmp object CLIENT_LAN object SERVER_A echo
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq ssh
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq https
access-list OUTSIDE_IN extended permit udp object CLIENT_LAN object SERVER_A range 33434 33463
access-group OUTSIDE_IN in interface outside
```

Everything else falls to the implicit deny. `packet-tracer` for `tcp/80` returns
`Action: drop` with the ACL named as the reason, and the deny is recorded in the
syslog against the **real** address, because logging is enabled on this ASA. Two
of these ACEs can only ever be proved as far as the firewall — see "What this lab
does not prove" below.

**The fourth ACE is a deliberate exception, not part of the policy.** UDP
33434–33463 is the Cisco traceroute probe range. The policy this lab states is
ICMP echo, SSH and HTTPS to one host and nothing else; that line sits outside it
and exists only so the traceroute section below actually works from a router. It
is declared here rather than left to be found later.

## Why traceroute works here

In the published version of this lab the traceroute was explained away instead of
being made to work. Three separate reasons, all of them fixed here:

1. **The ASA does not decrement the TTL by default.** A firewall that does not
   decrement it never generates the "time exceeded" a traceroute hop is made of,
   so it never appears as a hop at all. `set connection decrement-ttl` under
   `class-default` is what puts it in the hop list.
2. **The ICMP replies were not allowed back in.** `inspect icmp` builds the
   return connection for an echo, instead of requiring a matching ACL on the way
   back.
3. **The intermediate hops' ICMP errors never got out.** `inspect icmp error` is
   what lets a "time exceeded" raised behind the firewall reach the client, and
   it rewrites the IP header embedded inside it so the addresses line up with
   the translation. Without it those hops come back as stars.

To that, add the UDP range in the ACL above. The probe has to leave from the
client LAN, because that is the only source the ACL permits — hence the
`source` keyword below. The result, with the server in Site-A:

```
R-Client# traceroute 198.51.100.8 source GigabitEthernet0/1 probe 1 timeout 2
Tracing the route to 198.51.100.8
  1 203.0.113.2 1 msec
  2 192.0.2.2 2 msec
  3 198.51.100.8 2 msec
```

With the server in Site-B the trace is one hop longer: `203.0.113.2`,
`192.0.2.2`, `192.0.2.6`, `198.51.100.8`.

**This has a price, and it belongs in the open.** `inspect icmp error` makes
internal hops visible to an external client: `192.0.2.2` and `192.0.2.6` are
inside transit addresses and they show up in a trace run from outside the
firewall. That is the trade — a working traceroute in exchange for exposing the
internal path. A production firewall would have to decide which of the two it
wants; this lab chooses the traceroute and says so.

## What this lab does not prove

**Server-A is a VPCS. It does not serve SSH and it does not serve HTTPS.** It
answers ICMP echo, and that is the whole of its repertoire. So the SSH and HTTPS
ACEs cannot be demonstrated by connecting to a service, and nothing here claims
otherwise.

What *is* demonstrated is the firewall's half of the job: that the policy
**permits** those ports and **translates** them all the way to the real address.
`packet-tracer` for `tcp/22` and for `tcp/443` ends in `Action: allow`, and the
corresponding ACE hit counters move. The translation down to `10.100.100.10` is
carried by `show nat detail` and by the expanded ACL rather than by the retained
`packet-tracer` evidence — [`verification.md`](verification.md) §7 says exactly
which output proves which half. Whether a server on the far end answers is out
of scope.

## What was wrong in the published version

This lab was rebuilt from scratch. Eight things are different from the version
that is on GitHub, and each one is a defect that was found and corrected rather
than a stylistic preference.

1. **The NAT rule was incomplete.** It ended at the mapped object, and the ASA
   rejects that with `Incomplete command` — so nothing was configured and the
   `SERVER_A` object was left unused by anything at all. The complete rule ends
   `... destination static VIP_SERVER_A SERVER_A`.
2. **The ACL matched the mapped address.** Since ASA 8.3 an interface ACL is
   evaluated *after* the destination NAT has been undone, that is, against the
   **real** address. `permit tcp any host <virtual IP>` therefore never matches
   anything. The rebuilt ACL uses the `SERVER_A` object, which also makes the
   lab's promise true — move the server and the ACL follows on its own.
   `show access-list` shows it expanded to `host 10.100.100.10`.
3. **OSPF no longer crosses the firewall.** The ASA speaks OSPF on `inside` only,
   with MD5 authentication, and R-Client keeps a plain default route toward the
   firewall. Verified: R-Client forms no adjacency and learns no internal prefix.
4. **There is a real client LAN** behind R-Client (`203.0.113.32/27`, PC-Ext at
   `.34`), and the NAT source object is that subnet rather than a `/32`.
5. **Traceroute works**, rather than being explained away: `inspect icmp`,
   `inspect icmp error` and `set connection decrement-ttl`.
6. **Addressing.** Everything public-facing is now in RFC 5737 documentation
   space. The virtual address moved from `8.8.8.8` to `198.51.100.8`, and the ISP
   network from `4.4.4.0/29` to `198.51.100.0/29`.
7. **Logging, SSH and a stray route.** The ASA now has logging enabled, so a deny
   leaves a trace. The switches have working SSH: the published configs had
   `login` with no password, which rejects every attempt, plus orphan
   `ip ssh server algorithm` lines with no RSA key and no local user. SW-B's
   loose default route, which was never redistributed and which SW-A therefore
   never saw, is gone — everything internal is learned by OSPF.
8. **The ASA needs `console serial`.** Without it the ASAv boots perfectly and
   its serial console goes mute forever after the boot loader: the device works,
   answers pings, and cannot be talked to.

## Design decisions worth knowing

**OSPF lives entirely inside the firewall.** One process, area 0, MD5
authentication on every transit link. The speakers are the ASA (on `inside`
only, router-id `10.255.0.254`), SW-A, SW-B and R-ISP. Three adjacencies form —
ASA–SW-A, SW-A–SW-B, SW-B–R-ISP — so the ASA and R-ISP see one neighbour each
and the two switches see two. R-Client sees none at all, and that is the point:
an external client should not be handed a copy of the internal topology.

**Router IDs are pinned to loopbacks** (`10.255.0.1`, `.2`, `.3`) so they cannot
drift when an interface changes. The ASA has no loopback interface and pins its
router-id explicitly.

**The user VLAN SVIs are passive.** `Vlan10` on both switches is advertised into
area 0 without sending hellos into a VLAN where nothing would answer. The same
applies to `R-ISP Gi0/0`, which faces only SRV-ISP.

**SSH key exchange is `dh-group14-sha1`.** ASA 9.9(2) offers exactly two groups,
`dh-group1-sha1` and `dh-group14-sha1`; group 14 is 2048-bit Diffie-Hellman and
is the strongest available on that train. This lab does not claim SHA-256 — that
arrived in later releases.

**Public-facing addressing uses RFC 5737 documentation ranges**
(`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`), and the internal sites use
RFC 1918. The lab can be imported anywhere without colliding with a real network,
and no address in it points at something that exists — which is exactly why the
virtual address is `198.51.100.8` and not a real public IP.

## Platform notes

Both of these cost time and are stated here rather than hidden.

**`console serial` on the ASAv is not decoration.** Without it the ASAv sends its
console to the virtual VGA and EVE-NG's serial port stays silent after the boot
loader. It is in the skeleton config for that reason.

**A `Vlan` SVI created by an injected startup-config comes up `down/down`** on
IOSvL2, even with the VLAN active and its access ports forwarding. Neither
`no shutdown` nor bouncing a port fixes it; the SVI has to be removed and
recreated by hand. The tell is the `Method` column of
`show ip interface brief`: `TFTP` while it is broken, `manual` once recreated.

## What you practise

- Writing a twice-NAT rule on an ASA and reading `show nat detail` and
  `show xlate` to confirm what it actually built.
- Understanding **which** address an ASA interface ACL matches on a NAT'd flow —
  the real one — and why building the ACL out of network objects is what makes a
  server move painless.
- Using `packet-tracer` as the primary tool: proving that a permitted port is
  allowed end to end, and that a non-permitted one is dropped *by the ACL*
  specifically, without needing a real service to answer.
- Keeping a routing protocol on the correct side of a security boundary, and
  authenticating it.
- Getting `traceroute` to survive a firewall, and knowing what that costs.
- Reading ACL hit counters and syslog denials as evidence instead of assuming.

## What is in `configs/`

`configs/` holds what each of the five IOS and ASA devices actually runs, pulled
from the lab itself and sanitised. The five VPCS endpoints carry nothing beyond a
name and an address, so their files live only in `configs-skeleton/` and are
the finished state too. Secrets are replaced by a fixed-length `<REDACTED>` marker — never by
a run of asterisks matching the original length, which would leak exactly how
long each credential was. Every device is fully configured, and the automated run
in [`verification.md`](verification.md) passes all 45 checks with zero failures,
with Server-A in Site-B.

[`configs-skeleton/`](configs-skeleton/) is the other half of the story: the
clean starting point for every device — hostnames, interface descriptions,
addressing, loopbacks, the VLANs and the two ASA `nameif` interfaces — with no
OSPF, no objects, no NAT and no ACL. Load those as the startup configs to work
through the lab from scratch.

## Running the lab

1. Build the topology in EVE-NG from the interface map in
   [`addressing-plan.md`](addressing-plan.md): 10 nodes, 9 links. The `.unl`
   is deliberately not published — an EVE-NG export embeds every node's
   startup-config verbatim, and nothing goes into this repo that has not been
   through the sanitised `configs/`.
2. Load [`configs-skeleton/`](configs-skeleton) as the startup-configs to work
   through the lab yourself, or [`configs/`](configs) for the finished state —
   in those, the `secret`, `password` and `md5` values are redacted, so
   substitute your own. The VPCS files use VPCS syntax, not IOS.
3. Confirm all three node images are present under `/opt/unetlab/addons/qemu/`,
   including `asav-992`.
4. Start all nodes. The switches need about two minutes; the ASAv is slower still
   — give it time before deciding its console is dead.
5. Work through [`verification.md`](verification.md) in order.

If a node boots with the factory hostname (`Switch>`), its startup-config was not
applied: EVE-NG only injects it into a node that boots clean. Stop that node,
**Wipe** it, and start it again.

To move Server-A to the other site, stop Server-A, SW-B and SW-A first —
EVE-NG will not re-cable a running node — then follow "Moving Server-A between
sites" above.
