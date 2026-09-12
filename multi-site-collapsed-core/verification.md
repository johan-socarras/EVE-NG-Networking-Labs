# Verification — Multi-Site Collapsed-Core Enterprise Network

Run these in order. Each step assumes the previous one passed; if one fails, fix
it before moving on, because later checks depend on it.

Every number quoted as *Measured* was taken from the finished lab, not estimated.

Console ports are assigned by EVE-NG in node order starting at 32769 — see
[`addressing-plan.md`](addressing-plan.md). Reaching them with
`telnet <eve-ip> <port>` is usually quicker than the HTML5 console.

## 0. Nodes booted with their configuration

```
show running-config | include hostname
```

Expected: the device's own hostname on all ten IOS nodes. A node answering
`Switch>` booted with the factory config — EVE-NG only injects the
startup-config into a node that boots clean. Stop it, **Wipe** it, start it
again.

**Measured:** 14 of 14 nodes came up with their own hostname on the first boot.

If a node refuses to start at all (EVE-NG reports "started" but no QEMU process
appears), wipe it too. A recreated node reusing the same node ID also reuses the
old working directory, so wipe it once more after recreating it.

## 1. Addressing and interface state

On every device:

```
show ip interface brief | exclude unassigned
```

Expected — every listed interface `up/up`, matching
[`addressing-plan.md`](addressing-plan.md):

| Device | Expected addresses |
|---|---|
| RTR-DC-01 | `Gi0/0 10.0.0.1`, `Gi0/1 172.16.0.5`, `Gi0/2 172.16.0.1`, `Lo0 10.0.255.1` |
| RTR-A-01 | `Gi0/0 172.16.0.9`, `Gi0/1 172.16.0.2`, `Gi0/2 10.1.0.1`, `Lo0 10.1.255.1` |
| RTR-B-01 | `Gi0/0 172.16.0.6`, `Gi0/1 172.16.0.10`, `Gi0/2 10.2.0.1`, `Lo0 10.2.255.1` |
| CSW-DC-01 | `Gi0/0 10.0.0.2`, `Lo0 10.0.255.2`, `Vlan10/20/30/100/199` on `10.0.x.1` |
| CSW-A-01 | `Gi0/0 10.1.0.2`, `Lo0 10.1.255.2`, `Vlan10/20/30/100/199` on `10.1.x.1` |
| CSW-B-01 | `Gi0/0 10.2.0.2`, `Lo0 10.2.255.2`, `Vlan10/20/30/100/199` on `10.2.x.1` |
| ASW-DC-01 / -02 | `Vlan10 10.0.10.11` / `10.0.10.12` |
| ASW-A-01 / B-01 | `Vlan10 10.1.10.11` / `10.2.10.11` |

An interface showing `administratively down` is missing its `no shutdown`. One
that is `up/down` is cabled to the wrong peer — check the interface map.

**Measured:** all 37 expected addresses present, no interface down.
That is 4 on each router, 7 on each multilayer switch and 1 on each access
switch. The four VPCS endpoints are not in that count: they do not run IOS,
so they have no `show ip interface brief` to read.

## 2. EtherChannel

```
show etherchannel summary
```

Expected: every bundle `Po(SU)` with both members `(P)`. `S` = Layer 2,
`U` = in use, `(P)` = bundled. Protocol shows `-`, not `LACP`: these bundles are
static on purpose — see §10.

**Measured:** 8 port-channels, all `(SU)`, all 16 members `(P)`.

```
CSW-DC-01#show etherchannel summary
1      Po1(SU)          -        Gi0/1(P)    Gi1/0(P)
2      Po2(SU)          -        Gi0/2(P)    Gi1/1(P)
```

A member showing `(s)` — suspended — means the bundle is not forming. Check that
**both members carry identical switchport configuration**; one differing line is
enough.

## 3. Spanning tree

```
show spanning-tree vlan 10
```

Expected: the site's multilayer switch is root for every VLAN (priority 24576),
and the access switches see it as root.

**Measured:**

| Device | VLAN 10 |
|---|---|
| CSW-DC-01 | `This bridge is the root`, priority 24586 |
| ASW-DC-01 | root ID `5000.0004.0000` (CSW-DC-01), own priority 32778 |
| CSW-A-01 | `This bridge is the root`, priority 24586 |
| ASW-A-01 | root ID `5000.0005.0000` (CSW-A-01), own priority 32778 |

That the access switch sees the multilayer switch as root also proves STP BPDUs
cross the EVE-NG bridges — which matters for §10.

## 4. OSPF adjacencies

```
show ip ospf neighbor
show ip ospf interface brief
```

Expected across the whole lab: **three adjacencies**, one per site, both ends
`FULL`. Each of the six routed devices sees exactly **one** neighbour.

The transit links run `ip ospf network point-to-point`, so the `State` column
shows `FULL/  -` rather than `FULL/DR` — that is correct, not a fault.

**Measured:** 6 endpoints in FULL = 3 adjacencies, using the pinned loopback
router IDs:

| Device | Neighbour ID |
|---|---|
| RTR-DC-01 | `10.0.255.2` |
| CSW-DC-01 | `10.0.255.1` |
| RTR-A-01 | `10.1.255.2` |
| CSW-A-01 | `10.1.255.1` |
| RTR-B-01 | `10.2.255.2` |
| CSW-B-01 | `10.2.255.1` |

More than one neighbour on a device means something that should be passive is
not — most likely an SVI. Fewer means a link is down or one side is missing its
`ip ospf 1 area 0`, its authentication key, or its `network point-to-point`.

## 5. Inter-site routing, including the transit links

On each router:

```
show ip route static
```

Expected: two summarised `/16` routes, and only those two. The floating
backups have administrative distance 100, so while the tracked primaries are
up they are not installed in the RIB and this command does not show them —
`show running-config | include ^ip route` does.

**Measured:** 2 of 2 summaries present on all three routers.

Then the check the previous revision of this lab could not pass — reaching
another site's **point-to-point link**, not just its VLANs:

```
CSW-A-01#ping 10.0.0.2
CSW-DC-01#ping 10.2.0.2
```

**Measured:** 100% on all four tested pairs
(`CSW-A-01 → 10.0.0.2`, `CSW-B-01 → 10.0.0.2`, `CSW-DC-01 → 10.1.0.2`,
`CSW-DC-01 → 10.2.0.2`).

And end to end, with the full path visible:

```
CSW-A-01#traceroute 10.2.0.2
  1 10.1.0.1     (RTR-A-01)
  2 172.16.0.10  (RTR-B-01, across the A-B WAN link)
  3 10.2.0.2     (CSW-B-01)
```

## 6. VLAN 199 isolation

The isolated VLAN must allow ICMP between isolated segments and nothing else,
in **both** directions.

### What is permitted

From any isolated endpoint:

```
SRV-A-01> ping 10.0.199.10 -c 4
```

**Measured:** 4/4 on all six site pairs
(DC→A, DC→B, A→DC, A→B, B→DC, B→A).

### What is denied

VPCS can send TCP and UDP probes, which is what actually tests an ACL — a ping
that succeeds proves nothing about the rest:

```
SRV-A-01> ping 10.0.199.10 -P 6 -p 80 -c 3
SRV-A-01> ping 10.0.199.10 -P 17 -p 53 -c 3
```

Expected: **no reply from the destination**, and an ICMP type 3 code 13 from the
gateway. A denied packet does not vanish silently — the SVI answers:

```
*10.1.199.1 tcp_seq=1 ttl=255 time=3.355 ms (ICMP type:3, code:13,
 Communication administratively prohibited)
```

**Measured:** 0 replies from the destination and 2–3 `administratively
prohibited` messages per run, for both TCP/80 and UDP/53.

That the ICMP error reaches the host at all is the outbound ACL working as
designed: it permits `unreachable` and `ttl-exceeded` precisely so path errors
still get through.

### Counters

```
show access-lists ISOLATED-IN
```

**Measured** on CSW-A-01 after the six permitted pairs and the denied probes:

```
Extended IP access list ISOLATED-IN
    10 permit icmp 10.1.199.0 0.0.0.255 10.1.199.0 0.0.0.255
    20 permit icmp 10.1.199.0 0.0.0.255 10.0.199.0 0.0.0.255 (9 matches)
    30 permit icmp 10.1.199.0 0.0.0.255 10.2.199.0 0.0.0.255 (8 matches)
    40 deny ip any any log (12 matches)
```

The counters are cumulative across verification passes, which is why entries
20 and 30 read higher than the four pings of a single test. Entry 10 stays at
zero on purpose: it covers traffic that never leaves the local isolated
segment, so it is never exercised from another site.

Non-zero counters on both the permit and the deny are the point. An ACL that has
never matched anything has not been verified, only configured.

## 7. DHCP relay

`SRV-DC-02` sits in VLAN 20 and takes its address from RTR-DC-01 through the
relay on `CSW-DC-01 Vlan20`.

```
SRV-DC-02> ip dhcp
SRV-DC-02> show ip
RTR-DC-01#show ip dhcp binding
```

**Measured:** the endpoint moved from its skeleton static `10.0.20.50` to
`10.0.20.100` with `DOMAIN NAME : lab.example` learned from the pool, and the
router registered the lease:

```
10.0.20.100         0100.5079.6668.0c       Sep 10 2026 03:45 AM    Automatic
```

The skeleton static is deliberately inside the pool's excluded range, so an
address of `.100` can only have come from DHCP.

## 8. Management plane

### SSH into an access switch

The previous revision of this lab configured SSH on switches that had no
management SVI and no default gateway, so it could never be used. Now it can:

```
CSW-DC-01#ssh -l netadmin 10.0.10.11
```

**Measured:** works from both multilayer switches into their access switches
(`CSW-DC-01 → ASW-DC-01`, `CSW-A-01 → ASW-A-01`), reaching an enabled prompt and
running `show version`.

### The VTY ACL actually rejects

From a device whose source address is outside the management VLANs:

```
RTR-A-01#ssh -l netadmin 10.0.10.11
```

**Measured:** connection refused by `access-class MGMT-VTY in` — no password
prompt is ever offered.

### NTP

```
show ntp status
```

**Measured:** 10 of 10 devices synchronised. RTR-DC-01 is the reference at
stratum 3 (`ntp master 3`); the other nine sit at stratum 4 with
`reference is 10.0.255.1`.

NTP needs time. For the first several minutes the clients show
`Clock is unsynchronized` with `loopfilter state is 'FREQ' (Drift being
measured)` even though the association is already correct — that is normal, not
a fault. Give it fifteen minutes before concluding anything.

## 9. Failure test — the point of the WAN triangle

Shut the direct Site-A ↔ Data Center link and confirm traffic reroutes through
Site-B.

```
RTR-A-01(config)# interface GigabitEthernet0/1
RTR-A-01(config-if)# shutdown
```

**Measured:**

| | Before | Link down | Restored |
|---|---|---|---|
| `10.0.0.0/16` next hop on RTR-A-01 | `172.16.0.1` (direct) | `172.16.0.10` (via Site-B) | `172.16.0.1` |
| Path from CSW-A-01 | `10.1.0.1 → 172.16.0.1 → 10.0.0.2` | `10.1.0.1 → 172.16.0.10 → 172.16.0.5 → 10.0.0.2` | — |
| Ping SRV-A-01 → SRV-DC-01 | 5/5 | **8/8, no loss** | 5/5 |
| Track state | 2 Up | down after **10 s** | up after **20 s** |

Restore the interface before moving on, and do not save while it is shut.

**This test cannot pass without the IP SLA probes.** EVE-NG links are bridges and
a bridge does not propagate link-down: the far end stays `up/up`, the connected
route stays in the table, and an untracked static route is never withdrawn. The
failure then looks like a design bug when it is a simulator artefact.

### The limitation this test does not cover

If an entire **site router** fails rather than a link, the two surviving routers
each install their floating route toward the other, and packets for the dead site
loop until the TTL expires. That is the known cost of floating statics without a
routing protocol, and it is why Lab 02 runs OSPF end to end.

## 10. Troubleshooting notes

Real problems hit while building this lab, and what each one actually was.

**Port-channels stuck with members suspended.** Both ends configured
`channel-group N mode active`, both ends showing `(s)`, and `show lacp neighbor`
empty on both sides. It is not a configuration error: **LACP frames do not cross
the EVE-NG bridges.** Three tests isolate it — removing the `channel-group`
brings the plain trunk up with CDP working; identical LACP config on both ends
still shows no neighbour; `mode on` bundles immediately. STP and CDP cross the
same links fine, so it is specific to the slow-protocols multicast address LACP
uses. The bundles in this lab are static as a result.

**A second member suspended while the first bundles.** Different cause, same
symptom: the members of one port-channel must have **identical** switchport
configuration. Removing `switchport nonegotiate` from one member only is enough
to break it.

**`no channel-group 1` is rejected as incomplete.** On IOSvL2 the command is
`no channel-group`, with no number.

**`traceroute` missing its last hop.** Two separate causes, both harmless.
IOS answers the final hop from the interface the packet **arrives on**, not from
the destination address, so a traceroute to a device's far-side interface never
shows that address. And IOS rate-limits ICMP unreachables to one per 500 ms, so
two traceroutes fired back to back at the same target leave the last hop blank —
wait about ten seconds between runs.

**`!A` at the end of a traceroute into VLAN 199.** That is the isolation ACL
rejecting the UDP probe, which is correct behaviour and further proof the filter
works.

**Configuration applying extremely slowly on the routers only.** Automation that
waits for a `(config...)#` prompt stalls on `ip dhcp pool`, because the DHCP pool
sub-mode prompt is `(dhcp-config)#` — it does not start with `config`. The
switches, having no pools, were unaffected.

## 11. Result

| Area | Result |
|---|---|
| Nodes booted with their own configuration | 14 / 14 |
| Addressing and interface state | 37 addresses, 0 interfaces down |
| EtherChannel | 8 bundles `(SU)`, 16 members `(P)` |
| Spanning tree | multilayer switch root in all three sites |
| OSPF | 3 adjacencies, 6 endpoints FULL |
| Inter-site routing incl. transit `/30`s | 100% on 4 pairs, full traceroute |
| VLAN 199 permitted ICMP | 6 site pairs, 4/4 each |
| VLAN 199 denied TCP and UDP | 0 replies from destination, ACL counters non-zero |
| DHCP relay | lease issued and registered |
| SSH into an access switch | works; VTY ACL rejects other sources |
| NTP | 10 / 10 synchronised |
| WAN link failure | reroutes via Site-B, no packet loss |

**Total: 44 automated checks, 0 failures**, plus the six-point failure test.
