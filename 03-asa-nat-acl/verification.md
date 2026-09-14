# Verification — Lab 03

Run these in order. Each step assumes the previous one passed; if one fails, fix
it before moving on, because later checks depend on it.

**Nothing below is reconstructed from memory.** Read each block by its prompt:

- A block that opens with a device prompt (`ASA#`, `SW-B#`, `PC-Ext>`) is a raw
  transcript, shown as the device printed it. Each one is attributed where it is
  used, because they come from **three separate captures taken at three
  different moments** — which is why the counters in one do not continue the
  counters in another.
- A block with no prompt is either a configuration line quoted from
  [`configs/`](configs/), or — where it is labelled as such — the broken line
  from the published version of this lab.
- Where the only evidence retained is the automated harness's own result line,
  that line is shown instead and said to be one. The harness prints its check
  names in Spanish and its output is reproduced unedited rather than retyped;
  the numbers (hit counts, ping counts, hop lists, TTLs) are the evidence, and
  they are language-neutral.

The full run is **45 automated checks, 0 failures**.

Some harness lines carry a `FIX-n` tag. The numbering is the build script's,
which labels five of the rebuild's corrections: **FIX-1** the complete NAT rule,
**FIX-2** the ACL against the real address, **FIX-3** OSPF off the outside
interface and authenticated inside, **FIX-4** working SSH on the switches and
`dh-group14-sha1` on the ASA, **FIX-5** logging enabled and SW-B's stray default
route removed.

**Only three of those five are tagged in the run, because only three are
asserted by a check of their own:** FIX-1 in block 6, FIX-2 in block 7, FIX-3 in
block 3. FIX-5's logging half is exercised indirectly — the syslog check in
section 8 cannot pass on an ASA with logging off — but no check asserts that
SW-B's stray default route is gone, and **no check touches FIX-4 at all**: the
switches' SSH configuration and the ASA's key-exchange group are read out of
[`configs/`](configs/), not measured. The README lists all eight differences
from the published version.

Console ports are assigned by EVE-NG as `32768 + node id`:

| Node | Port | Node | Port |
|---|---|---|---|
| PC-Ext | 32769 | R-ISP | 32774 |
| R-Client | 32770 | SRV-ISP | 32775 |
| ASA | 32771 | PC-A | 32776 |
| SW-A | 32772 | Server-A | 32777 |
| SW-B | 32773 | Server-B | 32778 |

Reaching them with `telnet <eve-ip> <port>` is usually quicker than the HTML5
console.

Four things about the ASAv console specifically, all of which cost time here:

- Paging is disabled with `terminal pager 0`, **not** `terminal length 0`.
- The factory `enable` password is empty. Answer the `Password:` prompt with an
  empty line, not with the lab password.
- On the first boot the ASAv may ask
  `Pre-configure Firewall now through interactive prompts [yes]?`. If that is not
  answered `no`, the console stays inside the wizard and everything sent
  afterwards is swallowed by it.
- The configuration includes `console serial`. Without that line the ASAv boots
  perfectly well and its serial console stays mute forever — there is no error to
  read, because nothing is printed at all.

**Where Server-A is.** Server-A has **one** cable. It is plugged into the site it
lives in; the other site keeps its access port in VLAN 10, never shut down and
empty, described `Reserved for Server-A`. In the configurations published in
[`configs/`](configs/), and in the harness run reproduced in sections 1–9,
Server-A is in **Site-B** on `10.100.100.10` — that is the lab as shipped.
Section 10 is the move itself, and its two captures run in the other direction,
Site-B → Site-A. So every *harness* line quoted below reads `10.100.100.10`.
Section 4 additionally pastes one full `show nat detail` taken after the move,
labelled where it appears; that block is the only place before section 10 where
`192.168.1.10` shows up.

---

## 1. The ten nodes boot with their configuration

```
show running-config | include ^hostname|^: Hardware      (IOS and ASA)
show ip                                                  (VPCS)
```

Expected: each device answers with its own hostname, and each VPCS with its own
name and planned address. A node answering `Switch>` booted with the factory
config — EVE-NG only injects the startup-config into a node that boots clean.
Stop it, **Wipe** it, start it again.

**Measured** — 10 of 10, harness output:

```
1. Los equipos arrancaron con su configuracion
  OK    R-Client
  OK    SW-A
  OK    SW-B
  OK    R-ISP
  OK    ASA
  OK    PC-Ext
  OK    PC-A
  OK    Server-A
  OK    Server-B
  OK    SRV-ISP

2. Direccionamiento
  OK    R-Client tiene sus 2 direcciones
  OK    SW-A tiene sus 4 direcciones
  OK    SW-B tiene sus 4 direcciones
  OK    R-ISP tiene sus 3 direcciones
  OK    ASA outside 203.0.113.2 e inside 192.0.2.1
  OK    Server-A esta en Site-B con 10.100.100.10
```

That is 13 routed addresses on the four IOS nodes, the ASA's two interface
addresses, and Server-A on the address its site gives it. The full list is in
[`addressing-plan.md`](addressing-plan.md).

Server-A's own view of itself, pasted from the VPCS — from the same pre-move
capture used in section 10:

```
Server-A> show ip

NAME        : Server-A[1]
IP/MASK     : 10.100.100.10/24
GATEWAY     : 10.100.100.1
DNS         :
MAC         : 00:50:79:66:68:09
LPORT       : 20000
RHOST:PORT  : 127.0.0.1:30000
MTU         : 1500
```

---

## 2. OSPF lives inside the firewall only

The published version of this lab ran OSPF **through** the ASA, so the external
client learned the entire internal topology from the device that exists to hide
it. Here the ASA speaks OSPF on `inside` only, with MD5 authentication, and
R-Client keeps a single static default route.

```
ASA#      show ospf neighbor
SW-A#     show ip ospf neighbor
SW-B#     show ip ospf neighbor
R-ISP#    show ip ospf neighbor
R-Client# show ip ospf neighbor
R-Client# show ip route
```

Expected: **three adjacencies, six endpoints in FULL**, and nothing on
R-Client — ASA ↔ SW-A, SW-A ↔ SW-B, SW-B ↔ R-ISP. So the ASA and R-ISP see one
neighbour each, the two switches see two each, and R-Client sees none.

**Measured:**

```
3. OSPF vive solo dentro del firewall
  OK    ASA: una adyacencia, y por inside                      1 vecinos
  OK    SW-A: dos vecinos FULL
  OK    SW-B: dos vecinos FULL
  OK    R-ISP: un vecino FULL
  OK    R-Client: NINGUN vecino OSPF (FIX-3)

4. El cliente externo no conoce la red interna
  OK    R-Client no aprende ningun prefijo interno
  OK    R-Client solo tiene la ruta por defecto hacia el ASA
```

The ASA check is two assertions in one line: exactly one `FULL` neighbour, and
the word `inside` in the output — an adjacency formed on `outside` would fail it
even if the count were right.

The leak test is explicit: the harness greps R-Client's routing table for
`192.168.1.`, `10.100.100.`, `192.0.2.4` and `192.0.2.8` and fails if **any** of
them appears. None does. What R-Client has instead is one line, which the
harness matches against `S* 0.0.0.0/0 ... 203.0.113.2` in `show ip route`. It is
there because the configuration puts it there — the line below is quoted from
[`configs/R-Client.txt`](configs/R-Client.txt), not captured from the console:

```
ip route 0.0.0.0 0.0.0.0 203.0.113.2
```

---

## 3. Internal connectivity, between sites and out to the ISP

Before touching NAT, the inside has to work on its own. Site-A must reach Site-B
across the switch-to-switch `/30`, and both must reach the ISP's server on the
far side of R-ISP.

```
PC-A>     ping 10.100.100.11 -c 4      (Site-A  -> Server-B in Site-B)
PC-A>     ping 198.51.100.4  -c 4      (Site-A  -> SRV-ISP)
Server-B> ping 198.51.100.4  -c 4      (Site-B  -> SRV-ISP)
Server-B> ping 192.168.1.11  -c 4      (Site-B  -> PC-A)
```

**Measured** — 16 of 16 replies:

```
5. Conectividad interna
  OK    PC-A -> Server-B (Site-A a Site-B)                     4/4
  OK    PC-A -> servidor del ISP                               4/4
  OK    Server-B -> servidor del ISP                           4/4
  OK    Server-B -> PC-A                                       4/4
```

All four of these paths are learned by OSPF; none of them crosses the firewall.
If a first packet is lost while ARP resolves, that is normal — the harness passes
a check at 3 replies out of 4 and still measured 4/4 on every pair.

---

## 4. The NAT rule is complete, and it translates

This is FIX-1. In the published lab the rule ended at the mapped object:

```
nat (outside,inside) source dynamic CLIENT_LAN interface destination static VIP_SERVER_A
```

The ASA rejects that with `Incomplete command`, so no rule was ever installed —
and the `SERVER_A` object, the one thing the whole lab is built around, was left
unused. A destination-static clause needs **both** halves: the mapped address the
client sends to, and the real address it becomes.

```
ASA# show running-config nat
ASA# show nat detail
```

Expected: the rule ends in `... destination static VIP_SERVER_A SERVER_A`, and
`show nat detail` shows non-zero counters plus the destination translation.

**Measured**, with Server-A in Site-B:

```
6. La regla de NAT esta completa y traduce
  OK    nat ... destination static VIP_SERVER_A SERVER_A (FIX-1)
  OK    la regla acumula aciertos                              translate_hits = 44, untranslate_hits = 68
  OK    Destination Origin 198.51.100.8 -> Translated 10.100.100.10
```

And the full command output, pasted from the run in Site-A (section 10), where
the same rule had been re-pointed by changing one line:

```
ASA# show nat detail
Manual NAT Policies (Section 1)
1 (outside) to (inside) source dynamic CLIENT_LAN interface  destination static VIP_SERVER_A SERVER_A
    translate_hits = 21, untranslate_hits = 30
    Source - Origin: 203.0.113.32/27, Translated: 192.0.2.1/30
    Destination - Origin: 198.51.100.8/32, Translated: 192.168.1.10/32
```

Read the two halves separately:

- **Source**, dynamic: the client LAN `203.0.113.32/27` is PATed to the ASA's
  inside address `192.0.2.1`. That is what makes the return traffic come back to
  the firewall without any internal device needing a route to the client LAN.
- **Destination**, static: `198.51.100.8` becomes the server's real address. This
  is the direction the lab is about, and it is a *twice* NAT — both halves are
  evaluated as one rule, which is why the flags in `show xlate` read `sT`.

`untranslate_hits` runs ahead of `translate_hits` in both captures — 68 against
44 in the harness run, 30 against 21 here. The un-NAT half is consulted for
inbound packets that the ACL then drops, so the two are not expected to match;
what the check actually requires is only that `untranslate_hits` is non-zero.

> **Note on syntax.** `show running-config object network SERVER_A` is *not* a
> valid command, and the ASA is unhelpful about it — this is pasted from the
> capture:
>
> ```
> ASA# show running-config object network SERVER_A
>                                         ^
> ERROR: % Invalid input detected at '^' marker.
> ```
>
> Use `show running-config object id SERVER_A`, or read the object out of
> `show running-config object`.

---

## 5. The ACL is evaluated against the REAL address

This is FIX-2, and it is the subtlest error in the published lab. That version
filtered on the mapped address:

```
access-list OUTSIDE_IN extended permit tcp any host <virtual IP>
```

Since ASA 8.3 the firewall **undoes destination NAT before the interface ACL is
evaluated**, so an ACE written against the virtual address can never match. The
lab appeared to work only because it was never tested with a packet.

The fix is to write the ACL against the object:

```
access-list OUTSIDE_IN extended permit icmp object CLIENT_LAN object SERVER_A echo
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq ssh
access-list OUTSIDE_IN extended permit tcp object CLIENT_LAN object SERVER_A eq https
access-list OUTSIDE_IN extended permit udp object CLIENT_LAN object SERVER_A range 33434 33463
```

which also makes the lab's promise true: move the server, change `SERVER_A`, and
the ACL follows on its own (section 10).

```
ASA# show access-list OUTSIDE_IN
```

Expected: the object expands to `host 10.100.100.10`, no ACE reads
`host 198.51.100.8` — that exact string is what the harness asserts is absent —
and at least one ACE has a non-zero counter.

**Measured:**

```
7. La ACL se evalua contra la direccion REAL (FIX-2)
  OK    la ACL expande el objeto a host 10.100.100.10
  OK    y NO contiene la direccion virtual
  OK    hay ACE con contador distinto de cero                  hitcnts=[14, 4, 1]
```

`hitcnts` is the harness printing the *distinct* hit counts it found across the
four ACEs, highest first — three values for four ACEs means two of them sat on
the same count, and no zero appears among them.

The expansion itself comes from a **different capture**: the one taken
immediately before the site move in section 10. Same lab, same Site-B state, but
a separate reading, so its counters stand on their own and are not a
continuation of the `[14, 4, 1]` above.

```
ASA# show access-list OUTSIDE_IN | include host
  access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 10.100.100.10 echo (hitcnt=7) 0xe1c229d2
  access-list OUTSIDE_IN line 2 extended permit tcp 203.0.113.32 255.255.255.224 host 10.100.100.10 eq ssh (hitcnt=1) 0xd3bb13eb
  access-list OUTSIDE_IN line 3 extended permit tcp 203.0.113.32 255.255.255.224 host 10.100.100.10 eq https (hitcnt=1) 0xcb38724a
  access-list OUTSIDE_IN line 4 extended permit udp 203.0.113.32 255.255.255.224 host 10.100.100.10 range 33434 33463 (hitcnt=4) 0xa2e2667b
```

Two things to notice, because they are the whole point of this section:

1. The object names are gone. The running ACL is expanded to literal addresses,
   and the literal address is the **real** one, `10.100.100.10`. `198.51.100.8`
   is nowhere in the expansion — an ACL written against it would sit at
   `hitcnt=0` forever.
2. Every hit counter is non-zero. An ACL that has never matched anything has been
   configured, not verified.

The fourth ACE, the UDP range, is a **deliberate exception** to the
ICMP/SSH/HTTPS-only policy. It exists so the traceroute in section 9 works. See
[Deliberate exceptions](#deliberate-exceptions-and-known-limits).

---

## 6. The external client reaches the virtual address

```
PC-Ext> ping 198.51.100.8 -c 4
ASA#    show xlate
```

Expected: replies from `198.51.100.8`, and a static translation in `show xlate`
mapping the inside real address to the outside virtual one.

**Measured** — 4 of 4. The ping and the `show xlate` below are pasted from the
pre-move capture of section 10; they appear here because this is the section
they belong to, not because they are a second, independent run:

```
PC-Ext> ping 198.51.100.8 -c 4

84 bytes from 198.51.100.8 icmp_seq=1 ttl=60 time=2.590 ms
84 bytes from 198.51.100.8 icmp_seq=2 ttl=60 time=3.358 ms
84 bytes from 198.51.100.8 icmp_seq=3 ttl=60 time=2.148 ms
84 bytes from 198.51.100.8 icmp_seq=4 ttl=60 time=2.600 ms
```

```
ASA# show xlate
6 in use, 9 most used
Flags: D - DNS, e - extended, I - identity, i - dynamic, r - portmap,
       s - static, T - twice, N - net-to-net
NAT from inside:10.100.100.10 to outside:198.51.100.8
    flags sT idle 0:00:27 timeout 0:00:00

ICMP PAT from outside:203.0.113.34/12583 to inside:192.0.2.1/12583 flags ri idle 0:00:30 timeout 0:00:30
UDP PAT from outside:203.0.113.33/49157 to inside:192.0.2.1/49157 flags ri idle 0:00:27 timeout 0:00:30
UDP PAT from outside:203.0.113.33/49156 to inside:192.0.2.1/49156 flags ri idle 0:00:27 timeout 0:00:30
UDP PAT from outside:203.0.113.33/49155 to inside:192.0.2.1/49155 flags ri idle 0:00:27 timeout 0:00:30
UDP PAT from outside:203.0.113.33/49154 to inside:192.0.2.1/49154 flags ri idle 0:00:27 timeout 0:00:30
```

The first entry is the lab. `flags sT` = **s**tatic, **T**wice — one rule doing
both halves. `timeout 0:00:00` means it never ages out; it exists because the
rule exists, not because traffic created it.

Everything below it is the source half doing its job: the client's ICMP and the
UDP traceroute probes, PATed behind `192.0.2.1`. The `r` flag is portmap and `i`
is dynamic — those *do* age out, at 30 seconds.

The harness runs the same two checks:

```
8. El cliente externo alcanza la IP virtual
  OK    PC-Ext -> 198.51.100.8                                 4/4
  OK    show xlate enseña la traduccion estatica
```

Its second check asserts both halves of the string —
`inside:10.100.100.10` **and** `outside:198.51.100.8` — so a translation to the
wrong address would fail it.

---

## 7. packet-tracer: HTTPS and SSH are permitted and translated

Server-A is a VPCS. It answers ICMP and it serves nothing else — no SSH daemon,
no web server. What can be demonstrated, and what is demonstrated here, is that
**the firewall permits those two protocols and translates them all the way to the
real address**. Whether a service answers is out of scope for this lab, and
section [Not tested](#not-tested) says so rather than pretending otherwise.

```
ASA# packet-tracer input outside tcp 203.0.113.34 1234 198.51.100.8 443
ASA# packet-tracer input outside tcp 203.0.113.34 1234 198.51.100.8 22
```

Expected: `Action: allow` on both, with the UN-NAT phase rewriting the
destination to `10.100.100.10`.

**Measured** — these two lines belong to the harness's own block 8, alongside the
two quoted in section 6:

```
  OK    packet-tracer HTTPS (tcp/443) -> allow hasta 10.100.100.10
  OK    packet-tracer SSH (tcp/22) -> allow hasta 10.100.100.10
```

**Read that check name carefully.** It says "allow hasta 10.100.100.10", but the
only thing the harness asserts is that `Action: allow` appears in the ASA's
output. It does not parse the `UN-NAT` phase, and no full `packet-tracer`
transcript was retained — the real address in the check name comes from the
harness's own topology data, not from the device's answer. What carries the
translation claim is pasted output elsewhere: section 4, where `show nat detail`
reads destination `198.51.100.8` → the real address, and section 5, where the ACE
is expanded to the real host.

Run the commands yourself to read the phase list; the phases that matter are
`UN-NAT` (static translation to the real address) and `ACCESS-LIST` (matching the
expanded ACE from section 5). The ACL counters in section 5 move when you do.

---

## 8. Negative test: what the ACL does not permit is dropped

An ACL is only verified when something has been refused by it. Same source, same
virtual destination, a port the policy does not list:

```
ASA# packet-tracer input outside tcp 203.0.113.34 1234 198.51.100.8 80
ASA# show logging | include 106023
```

Expected: `Action: drop`, with the ACL named as the reason, and a syslog entry
recording the deny **against the real address** — because, as in section 5, by
the time the ACL is evaluated the destination has already been un-NATed.

**Measured:**

```
9. Lo que la ACL no permite se cae
  OK    packet-tracer tcp/80 -> drop
  OK    y la razon es la ACL
  OK    el syslog registra el deny contra la direccion real
```

Three separate assertions, and the third is the interesting one. It requires two
things in the same output: the message ID `106023` — the ASA's
`Deny protocol src ... dst ... by access-group` — and the string
`10.100.100.10`. A syslog line quoting `198.51.100.8` would fail this check, and
it would mean the ACL was being evaluated against the mapped address, which is
the bug FIX-2 exists to remove.

As with section 7, the capture is the assertion rather than the raw log line;
`show logging | include 106023` prints it on a running lab. Note that this check
depends on FIX-5 — the published lab had no `logging enable`, so the ASA kept no
record of anything it denied.

---

## 9. Traceroute, with the ASA as the first hop

```
R-Client# traceroute 198.51.100.8 source GigabitEthernet0/1 probe 1 timeout 2
```

Expected: hops all the way to the virtual address, and the ASA at hop 1.

**Measured**, with Server-A in Site-B:

```
10. El traceroute devuelve saltos
  OK    traceroute llega a la IP virtual                       saltos=['203.0.113.2', '192.0.2.2', '192.0.2.6', '198.51.100.8']
  OK    el ASA aparece como primer salto (decrement-ttl)       primero=['203.0.113.2']
```

Four hops: the ASA outside interface, SW-A, SW-B, then the server behind its
virtual address. Reading them left to right is reading the path the packet takes
through the lab.

Three configuration items are required for this to work at all. They are the
traceroute correction — item 5 in the README's list of what the published lab got
wrong. They carry no `FIX-n` tag because no single automated check isolates them;
what proves them is the hop list above:

| Line | Without it |
|---|---|
| `inspect icmp` | return ICMP is not associated with the flow |
| `inspect icmp error` | the intermediate hops' ICMP errors are dropped by the ASA |
| `set connection decrement-ttl` | the ASA is invisible — it does not appear as a hop at all |

Plus the fourth ACE from section 5, permitting UDP 33434–33463 inbound, since
IOS traceroute probes with UDP.

**The cost, stated plainly:** `inspect icmp error` is what makes the internal
transit addresses `192.0.2.2` and `192.0.2.6` visible to an external client. A
firewall that hides its inside does not normally let those errors through. This
lab chooses a working traceroute over that concealment, and the traceroute above
is what that choice looks like from outside.

---

## 10. The test the lab exists for: moving Server-A between sites

The promise is that the external client always reaches Server-A at
`198.51.100.8`, and that moving the server between sites costs **one line** on the
firewall — with the client untouched and the ACL untouched.

Server-A has one cable. It is not connected to both sites with one leg shut; a
server is not in two cities at once. Moving it is re-plugging the real cable, and
the site it leaves keeps its access port in VLAN 10, never shut down and empty,
waiting for it. That makes the EVE-NG side of the move a real step rather than something a
pre-built topology does for you: the three nodes the cable touches have to be stopped, the
old link deleted and a new one drawn — on the canvas, or through the API with
`visibility: 1` on the new network. It is the correct price for representing the
move honestly.

### Before: Server-A in Site-B

The cabling, pasted from both switches:

```
SW-B# show running-config interface GigabitEthernet0/0
Building configuration...

Current configuration : 164 bytes
!
interface GigabitEthernet0/0
 description To Server-A eth0
 switchport access vlan 10
 switchport mode access
 negotiation auto
 spanning-tree portfast edge
end
```

```
SW-A# show running-config interface GigabitEthernet0/0
Building configuration...

Current configuration : 201 bytes
!
interface GigabitEthernet0/0
 description Reserved for Server-A - no cable, server is in Site-B
 switchport access vlan 10
 switchport mode access
 negotiation auto
 spanning-tree portfast edge
end
```

Same VLAN, same access configuration, same portfast — the difference between the
two ports is a cable, not a config. The harness checks this too:

```
2b. Server-A tiene UN SOLO cable, y la otra sede lo espera
  OK    SW-B Gi0/0 va a Server-A
  OK    SW-A Gi0/0 esta reservado y sin cable
  OK    y sigue siendo un puerto de acceso de la VLAN 10
```

State of the firewall before the move — the static entry only; the same capture
in full, with the PAT entries under it, is in section 6:

```
ASA# show xlate
NAT from inside:10.100.100.10 to outside:198.51.100.8
    flags sT idle 0:00:27 timeout 0:00:00
```

```
ASA# show access-list OUTSIDE_IN | include host
  access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 10.100.100.10 echo (hitcnt=7) 0xe1c229d2
  access-list OUTSIDE_IN line 2 extended permit tcp 203.0.113.32 255.255.255.224 host 10.100.100.10 eq ssh (hitcnt=1) 0xd3bb13eb
  access-list OUTSIDE_IN line 3 extended permit tcp 203.0.113.32 255.255.255.224 host 10.100.100.10 eq https (hitcnt=1) 0xcb38724a
  access-list OUTSIDE_IN line 4 extended permit udp 203.0.113.32 255.255.255.224 host 10.100.100.10 range 33434 33463 (hitcnt=4) 0xa2e2667b
```

And the client, from outside, reaching the virtual address — the same capture
quoted in section 6:

```
PC-Ext> ping 198.51.100.8 -c 4

84 bytes from 198.51.100.8 icmp_seq=1 ttl=60 time=2.590 ms
84 bytes from 198.51.100.8 icmp_seq=2 ttl=60 time=3.358 ms
84 bytes from 198.51.100.8 icmp_seq=3 ttl=60 time=2.148 ms
84 bytes from 198.51.100.8 icmp_seq=4 ttl=60 time=2.600 ms
```

### The move

1. **Stop the three nodes that touch the cable first** — Server-A, SW-B and
   SW-A. EVE-NG will not re-cable a running node, and that is what the recorded
   move did.
2. In the EVE-NG canvas, unplug Server-A `eth0` from **SW-B Gi0/0** and plug it
   into **SW-A Gi0/0**. Start the three nodes again and give them a few minutes
   to come back before touching anything else.
3. Swap the two port descriptions so they keep telling the truth: the port that
   now has the server reads `To Server-A eth0`, and the one that lost it reads
   `Reserved for Server-A - no cable, server is in Site-A`.
4. Re-address the VPCS for its new site:
   `ip 192.168.1.10/24 192.168.1.1`
5. On the ASA, change **one line** — the host inside the object. The
   `description` is rewritten in the same breath, but that is bookkeeping; the
   `host` line is the change:

   ```
   object network SERVER_A
    host 192.168.1.10
    description Server-A real address - currently in Site-A
   ```

6. `clear xlate`, so the existing static translation is rebuilt against the new
   real address.

The client is not touched. The ACL is not touched. The NAT rule is not touched —
only the object it points at.

### After: Server-A in Site-A

The client, unchanged, still reaching the same address:

```
PC-Ext> ping 198.51.100.8 -c 4

84 bytes from 198.51.100.8 icmp_seq=1 ttl=61 time=2.647 ms
84 bytes from 198.51.100.8 icmp_seq=2 ttl=61 time=1.831 ms
84 bytes from 198.51.100.8 icmp_seq=3 ttl=61 time=1.660 ms
84 bytes from 198.51.100.8 icmp_seq=4 ttl=61 time=2.003 ms
```

```
ASA# show xlate
5 in use, 9 most used
Flags: D - DNS, e - extended, I - identity, i - dynamic, r - portmap,
       s - static, T - twice, N - net-to-net
NAT from inside:192.168.1.10 to outside:198.51.100.8
    flags sT idle 0:00:01 timeout 0:00:00

ICMP PAT from outside:203.0.113.34/62248 to inside:192.0.2.1/62248 flags ri idle 0:00:01 timeout 0:00:30
ICMP PAT from outside:203.0.113.34/61992 to inside:192.0.2.1/61992 flags ri idle 0:00:02 timeout 0:00:30
ICMP PAT from outside:203.0.113.34/61736 to inside:192.0.2.1/61736 flags ri idle 0:00:03 timeout 0:00:30
ICMP PAT from outside:203.0.113.34/61480 to inside:192.0.2.1/61480 flags ri idle 0:00:04 timeout 0:00:30
```

```
ASA# show access-list OUTSIDE_IN | include host
  access-list OUTSIDE_IN line 1 extended permit icmp 203.0.113.32 255.255.255.224 host 192.168.1.10 echo (hitcnt=4) 0xe1c229d2
  access-list OUTSIDE_IN line 2 extended permit tcp 203.0.113.32 255.255.255.224 host 192.168.1.10 eq ssh (hitcnt=0) 0xd3bb13eb
  access-list OUTSIDE_IN line 3 extended permit tcp 203.0.113.32 255.255.255.224 host 192.168.1.10 eq https (hitcnt=0) 0xcb38724a
  access-list OUTSIDE_IN line 4 extended permit udp 203.0.113.32 255.255.255.224 host 192.168.1.10 range 33434 33463 (hitcnt=0) 0xa2e2667b
```

**The ACL re-expanded itself.** Compare it line for line with the "before"
output: same four lines, same line numbers, same hash values on the right
(`0xe1c229d2`, `0xd3bb13eb`, `0xcb38724a`, `0xa2e2667b`) — and every
`host 10.100.100.10` is now `host 192.168.1.10`. Not one `access-list` command
was entered. The ACEs reference the object; the object changed; the ACL followed.
That is the entire argument for FIX-2 in one diff.

The counters reset to reflect the new expansion, and the ICMP ACE is already at
`hitcnt=4` from the four pings above.

The NAT rule, likewise untouched, now translating to the other site:

```
ASA# show nat detail
Manual NAT Policies (Section 1)
1 (outside) to (inside) source dynamic CLIENT_LAN interface  destination static VIP_SERVER_A SERVER_A
    translate_hits = 21, untranslate_hits = 30
    Source - Origin: 203.0.113.32/27, Translated: 192.0.2.1/30
    Destination - Origin: 198.51.100.8/32, Translated: 192.168.1.10/32
```

### The physical proof: the path got shorter

Configuration can be argued with. The path cannot:

```
R-Client# traceroute 198.51.100.8 source GigabitEthernet0/1 probe 1 timeout 2
Type escape sequence to abort.
Tracing the route to 198.51.100.8
VRF info: (vrf in name/id, vrf out name/id)
  1 203.0.113.2 1 msec
  2 192.0.2.2 2 msec
  3 198.51.100.8 2 msec
```

| | Server-A in Site-B | Server-A in Site-A |
|---|---|---|
| Hop 1 | `203.0.113.2` (ASA outside) | `203.0.113.2` (ASA outside) |
| Hop 2 | `192.0.2.2` (SW-A) | `192.0.2.2` (SW-A) |
| Hop 3 | `192.0.2.6` (SW-B) | `198.51.100.8` (the server) |
| Hop 4 | `198.51.100.8` (the server) | — |
| Reply TTL at PC-Ext | `ttl=60` | `ttl=61` |

**SW-B is gone from the path.** The server used to be reached by crossing from
Site-A into Site-B; now it is one hop past SW-A, because it is physically in
Site-A. The TTL seen by the external client rises by exactly one for the same
reason. Neither number could change if the "move" were a shutdown of one leg of a
dual-homed server — which is precisely why this lab gives Server-A a single
cable.

And through all of it, `198.51.100.8` never changed. The external client was
never reconfigured, and never knew.

---

## Result

| Area | Result |
|---|---|
| Nodes booted with their own configuration | 10 / 10 |
| Addressing (4 IOS nodes, ASA, Server-A) | 6 / 6 checks, no missing address |
| One cable, one reserved empty port | 3 / 3 checks |
| OSPF adjacencies, all internal | 3 adjacencies, 6 endpoints FULL |
| R-Client isolation | 0 OSPF neighbours, 0 internal prefixes, default route only |
| Internal connectivity | 4 pairs, 4/4 each |
| NAT rule complete and translating | `translate_hits = 44`, `untranslate_hits = 68` |
| ACL against the real address | expands to `host 10.100.100.10`, VIP absent, counters non-zero |
| External client → virtual address | 4/4, static `sT` xlate present |
| packet-tracer tcp/443 and tcp/22 | `Action: allow`, both |
| packet-tracer tcp/80 | `Action: drop`, ACL named, message `106023` logged against the real address |
| Traceroute | 4 hops, ASA first |
| Moving Server-A between sites | ACL re-expanded on its own, path shortened by one hop |

**Total: 45 automated checks, 0 failures**, plus the site-move test.

Two operational notes for anyone re-running this. NAT and ACL counters are zeroed
when the ASA restarts, so traffic has to be generated **before** they are read or
a healthy lab looks broken — that produced two false failures here. And OSPF
takes up to a minute after the configuration is applied to form all three
adjacencies; measuring before that reports failures that do not exist. The
harness waits for both.

---

## Deliberate exceptions and known limits

**The UDP 33434–33463 ACE is an exception on purpose.** The stated policy for
this lab is ICMP echo, SSH and HTTPS to Server-A and nothing else. The fourth ACE
opens the IOS traceroute probe range so section 9 works end to end. It is a
teaching decision, not an oversight; remove it and the policy is what it claims
to be, and the traceroute stops past the ASA.

**`inspect icmp error` leaks internal hops.** With it enabled, the external
client sees `192.0.2.2` and `192.0.2.6` — the internal transit links — in its
traceroute. That is information a production firewall would normally withhold. It
is the price of a traceroute that works, and it is paid knowingly.

**`ssh key-exchange group dh-group14-sha1` is the strongest available here.**
ASA 9.9(2) offers exactly two key-exchange groups, `dh-group1-sha1` and
`dh-group14-sha1`. Group 14 is 2048-bit DH instead of 1024-bit, so it is the
right choice on this train — but the hash is still SHA-1. Nothing in this lab
provides SHA-256 key exchange, and it should not be read as if it did. Later ASA
trains are where that lives.

---

## Not tested

**Server-A does not serve SSH or HTTPS.** It is a VPCS. It replies to ICMP and
runs no services at all. Sections 5 and 7 prove that the firewall **permits**
tcp/22 and tcp/443 from the client LAN and **translates** them to the server's
real address — `Action: allow` in `packet-tracer`, and non-zero counters on the
`eq ssh` and `eq https` ACEs. They do not prove that anything answered, because
nothing was ever listening. No TCP session was established, no banner was ever
seen, and no application-layer traffic crossed this lab in either direction.
Anyone wanting that end of the test should replace Server-A with an image that
runs a real service; the firewall configuration would not change.

**The raw `packet-tracer` and syslog transcripts were not captured.** For
sections 7 and 8 the evidence retained is the harness's assertion on the device
output — `Action: allow`, `Action: drop`, and message ID `106023` together with
`10.100.100.10` — rather than the full text the ASA printed. The commands are
given in those sections and reproduce on a running lab.

**Not exercised at all:** failure and convergence behaviour (no link or node was
failed in this lab — that is Lab 02's subject), throughput or connection-rate
limits, IPv6, and NAT for traffic originated **from** the inside toward the
external client. The rule verified here is `(outside,inside)`, which is the
inbound direction; the reverse direction is out of scope.
