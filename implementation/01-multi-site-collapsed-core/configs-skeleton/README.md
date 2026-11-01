# Skeleton configs — the starting point

These are the **starting** configurations, not the solution. They contain only
hostnames, interface descriptions, the addressing of the routed links and the
loopbacks. There is deliberately no `router ospf`, no VLANs or SVIs, no
`channel-group`, no static routes, no `ip sla`, no ACLs, no DHCP and no SSH.

Load these as the EVE-NG startup-configs when you want to work through the lab
yourself. The finished configurations live in [`../configs/`](../configs/).

A few things worth knowing before you start:

- `CSW-*` carry `ip routing`; `ASW-*` carry `no ip routing`. That is the split
  between the multilayer switches and the pure Layer 2 access switches.
- Only `Gi0/0` on each `CSW-*` is a routed port (`no switchport`). Everything
  else on the switches stays Layer 2.
- Unused interfaces come shut. Leave them that way, or park them in a dead VLAN.
- The VPCS files use VPCS syntax (`set pcname` / `ip <addr>/<prefix> <gateway>`),
  not IOS.
- `SRV-DC-02` starts with the static address `10.0.20.50`. That address is inside
  the DHCP pool's excluded range on purpose, so that once you build the relay you
  can tell a leased address apart from the one written here.
