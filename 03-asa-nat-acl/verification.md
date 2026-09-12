# Verification

This file documents the tests used to verify that the lab is working as expected.

## Test 1: Site-A to Site-B Connectivity

From PC-A:

```bash
ping 10.100.100.11
```

Result:

```text
84 bytes from 10.100.100.11 icmp_seq=1 ttl=62 time=7.945 ms
84 bytes from 10.100.100.11 icmp_seq=2 ttl=62 time=8.236 ms
84 bytes from 10.100.100.11 icmp_seq=3 ttl=62 time=8.334 ms
84 bytes from 10.100.100.11 icmp_seq=4 ttl=62 time=8.625 ms
84 bytes from 10.100.100.11 icmp_seq=5 ttl=62 time=8.745 ms
```

Status: Passed.

This confirms that Site-A can reach Site-B.

## Test 2: Site-A to External Server

From PC-A:

```bash
ping 4.4.4.4
```

Result:

```text
84 bytes from 4.4.4.4 icmp_seq=1 ttl=61 time=8.547 ms
84 bytes from 4.4.4.4 icmp_seq=2 ttl=61 time=7.735 ms
84 bytes from 4.4.4.4 icmp_seq=3 ttl=61 time=7.830 ms
84 bytes from 4.4.4.4 icmp_seq=4 ttl=61 time=8.775 ms
84 bytes from 4.4.4.4 icmp_seq=5 ttl=61 time=8.269 ms
```

Status: Passed.

This confirms that Site-A has connectivity to the external server network.

## Test 3: Site-B to External Server

From Server-B:

```bash
ping 4.4.4.4
```

Result:

```text
84 bytes from 4.4.4.4 icmp_seq=1 ttl=62 time=10.540 ms
84 bytes from 4.4.4.4 icmp_seq=2 ttl=62 time=5.047 ms
84 bytes from 4.4.4.4 icmp_seq=3 ttl=62 time=7.102 ms
84 bytes from 4.4.4.4 icmp_seq=4 ttl=62 time=7.952 ms
84 bytes from 4.4.4.4 icmp_seq=5 ttl=62 time=5.634 ms
```

Status: Passed.

This confirms that Site-B has connectivity to the external server network.

## Test 4: R-Client to Virtual Server-A IP

From R-Client:

```cisco
ping 8.8.8.8
```

Result:

```text
Sending 5, 100-byte ICMP Echos to 8.8.8.8, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 3/6/17 ms
```

Status: Passed.

This confirms that R-Client can reach the virtual destination IP `8.8.8.8`.

The ASA translates traffic destined to `8.8.8.8` to the current real IP address of Server-A.

## Test 5: Server-A Moved Between Sites

Server-A was tested in both locations:

* Site-A real IP: `192.168.1.10`
* Site-B real IP: `10.100.100.10`

After updating the ASA `SERVER_A` object to the correct current IP, traffic from R-Client to `8.8.8.8` continued to work.

Status: Passed.

## Traceroute Note

The traceroute test from R-Client to `8.8.8.8` did not return hop information.

This is expected in this lab because Cisco IOS traceroute uses UDP high ports by default, while the ASA outside ACL only permits ICMP, SSH, and HTTPS.

Since the lab requirement is to allow only ICMP, SSH, and HTTPS, the failed traceroute does not indicate that the lab is broken.

## Useful Verification Commands

Cisco IOS:

```cisco
show ip interface brief
show ip route
show ip ospf neighbor
ping
traceroute
```

Cisco ASA:

```cisco
show interface ip brief
show route
show ospf neighbor
show access-list
show nat
show xlate
show conn
```

## Final Result

The lab successfully verifies:

* Site-A to Site-B connectivity.
* Site-A and Site-B access to the external `4.4.4.4` server.
* R-Client access to `8.8.8.8`.
* ASA destination NAT to Server-A.
* Server-A reachability after moving between sites.
