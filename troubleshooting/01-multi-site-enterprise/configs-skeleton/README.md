# Skeleton configs — the base build

These are the **base** configurations the lab is built from, not the exercise and
not the solution. They contain hostnames, interface descriptions, the addressing
of the routed links and the loopbacks. There is deliberately no VLAN, no SVI, no
`channel-group`, no `router ospf`, no `standby`, no static route, no `ip sla`, no
ACL, no DHCP, no NAT and no SSH.

Two ways to use them:

- **To work through the whole lab yourself**, load them as the EVE-NG
  startup-configs and build the design in [`../addressing-plan.md`](../addressing-plan.md)
  from scratch.
- **To rebuild the troubleshooting exercise**, start here, apply the full
  configuration, then inject the faults. The configuration the devices boot with
  for the exercise lands in `../configs/` when the lab is built.

Things worth knowing before you start:

- `R*` and `ISP-1` are IOSv routers. `*-DIST-*` are IOSvL2 switches carrying
  `ip routing`; `*-ACC-*` are IOSvL2 switches carrying `no ip routing`. That is
  the split between the multilayer distribution layer and the pure Layer 2 access
  layer.
- Only `Gi0/0` on each `*-DIST-*` is a routed port (`no switchport`). Everything
  else on a switch stays Layer 2, including the ports that will become
  EtherChannel members.
- Interface names depend on the image. **IOSvL2** (the ten switches) uses EVE-NG's
  two groups of four, `Gi0/0`–`Gi0/3` and `Gi1/0`–`Gi1/3`. **IOSv** (the four
  routers) numbers straight through, `Gi0/0`–`Gi0/7`: the fifth port of a router
  is `Gi0/4`, and IOS rejects `Gi1/0` on it. Every node needing more than four
  ports is created with eight, except `ISP-1`, which has four.
- Every description names the remote device **and** the remote interface, and
  marks which bundle a port belongs to, so the wiring can be checked from the
  configs alone without opening the topology.
- Unused interfaces come shut. Leave them that way.
- The VPCS files use VPCS syntax (`set pcname`, then `ip dhcp` or
  `ip <addr>/<prefix> <gateway>`), not IOS. Six hosts are DHCP clients; the three
  on `.50` are static on purpose, so a leased address and a hardcoded one are
  never confused while troubleshooting.
- `SRV-HQ-1`, `SRV-DR-1` and `MGMT-1` sit in VLANs that have no DHCP pool. A host
  there getting a lease is a fault.
