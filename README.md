# DNS Cache Poisoning (CVE-2008-1447) - Attack & Defense

Experimental reproduction of Kaminsky-style DNS cache poisoning and design of a lightweight defense mechanism using nonce + hash-based query validation.

## Overview

This project reproduces [CVE-2008-1447](https://nvd.nist.gov/vuln/detail/CVE-2008-1447), a well-known DNS cache poisoning vulnerability in BIND9, and evaluates a lightweight mitigation technique.

The implementation includes:
- A working exploit based on transaction ID prediction and forged responses
- Wireshark-based analysis of attack and response flow
- A nonce + SHA256 hash-based validation mechanism
- Simulation of authoritative DNS response delay (Slow Resolver)

## Architecture

```
[Victim PC] → [Recursive DNS (BIND9 9.4.2-P1)] → [Authoritative DNS (Slow Resolver)]
                         ↑
                   [Attacker (forged responses)]
```

- **Victim**: sends DNS queries and monitors poisoning
- **Recursive DNS**: vulnerable BIND9 with fixed port and predictable TXID
- **Authoritative DNS**: lightweight DNS server (Python, dnslib)
- **Attacker**: sends millions of spoofed responses using Scapy and multithreading

## Components

| Role       | IP              | Description                              |
|------------|-----------------|------------------------------------------|
| Victim     | 192.168.56.101  | `normal_status.py`, `safe_status.py`     |
| Resolver   | 192.168.56.102  | BIND9 (fixed port: 33333), TTL lowered   |
| Attacker   | 192.168.56.103  | `attack.py`, multithreaded spoofing      |
| Authoritative | 192.168.56.104 | `slow_dns.py`, DNS reply delay (6s)     |

All nodes are isolated using VirtualBox Host-Only network.

## Exploit Scenario

1. Victim sends query to `rand9999.netsec.kr`
2. Attacker sends 3M+ forged DNS replies targeting the correct TXID
3. If TXID matches before real response arrives, cache is poisoned
4. Victim receives attacker's IP (e.g., `1.1.1.1`)

## Defense Model

- DNS query format: `{nonce}.{hash}.{domain}`
- Authoritative server recomputes expected hash using nonce+domain
- Invalid queries return NXDOMAIN
- TTL set to 3 seconds to minimize poisoning window

## Security Analysis

- TXID entropy: 2¹⁶
- Nonce (8 chars, base36): ~2⁴³
- Hash (10 base64 chars): ~2⁶⁰
- Combined: ~2¹¹⁹
- Adding source port randomization raises entropy to ~2¹³⁵

Poisoning with brute-force becomes infeasible.

## Running the Project

```bash
# Victim
$ python3 normal_status.py
$ python3 safe_status.py

# Attacker
$ python3 attack.py

# Dig manually
$ dig rand9999.netsec.kr @192.168.56.102 -p 33333
```

## Requirements

- Python 3.x
- dnslib
- scapy
- Ubuntu / Kali Linux on VirtualBox

## Authors

- 이재현 (JaeHyun Lee)
- 양동현 (DongHyun Yang)

## License

This project is for educational purposes only.
