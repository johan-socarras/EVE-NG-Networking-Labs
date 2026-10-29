# Skeleton configs — the starting point

These are the **starting** configurations, not the solution. They contain only
hostnames, interface descriptions, IP addressing and loopbacks. There is
deliberately no `router ospf`, no `standby` (HSRP), no user VLANs or SVIs, and
no `channel-group`.

Load these as the EVE-NG startup-configs when you want to work through the lab
yourself. The finished configurations live in [`../configs/`](../configs/).

The VPCS files use VPCS syntax (`set pcname` / `ip <addr>/<prefix> <gateway>`),
not IOS.
