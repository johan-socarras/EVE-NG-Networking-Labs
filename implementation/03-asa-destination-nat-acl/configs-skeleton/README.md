# Skeleton configs — the starting point

These are the **starting** configurations, not the solution. They contain only
hostnames, interface descriptions, IP addressing, the loopbacks, VLAN 10 with
its SVI on each switch, and the ASA's two `nameif` interfaces with their
security levels — plus the console-line and VTP housekeeping every lab here
carries. There is deliberately no `router ospf`, no static route, no
`object network`, no `nat`, no `access-list`, no `inspect icmp`, no SSH and no
logging.

Load these as the EVE-NG startup-configs when you want to work through the lab
yourself. The finished configurations live in [`../configs/`](../configs/).

A few things worth knowing before you start:

- The ASA file keeps `console serial`. It is not part of the exercise: without
  it the ASAv boots, forwards traffic, and its console goes silent right after
  the boot loader, so you can never log in.
- `SW-A Gi0/0` is a VLAN 10 access port with no cable on it. That is the
  reserved slot for Server-A, which ships in Site-B on `SW-B Gi0/0`.
- With no routing yet, only directly connected links work at first boot.
  R-Client's default route toward the ASA, the ASA's route back to the client
  LAN, and OSPF area 0 on the inside are all yours to add.
- The VPCS files use VPCS syntax (`set pcname` / `ip <addr>/<prefix> <gateway>`),
  not IOS.
