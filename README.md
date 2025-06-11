# DNS Cache Poisoning 실습 프로젝트

본 프로젝트는 **CVE-2008-1447 (Kaminsky Attack)** 기반 DNS Cache Poisoning 공격을 실험적으로 재현하고, 이에 대한 **lightweight 방어 모델**을 설계 및 적용하는 네트워크 보안 프로젝트입니다.

> 📌 과목: 네트워크 보안  
> 👨‍💻 팀원: 이재현, 양동현
> 🗓️ 프로젝트일: 2025. 04.27 ~ 2025.06.11

---

## 🔍 프로젝트 개요

- **목표:** BIND9 DNS 서버의 취약점을 이용한 DNS Cache Poisoning 공격의 원리를 실험적으로 분석하고, Wireshark를 통한 패킷 흐름 추적 및 해시 기반 방어 모델을 적용하여 공격 탐지 및 차단까지 수행.
- **핵심 기술:** Scapy, dnslib, threading, hashlib, Wireshark, VirtualBox

---

## 🧪 실습 구성

### 🔹 환경 구성

| 역할            | IP              | 주요 기능 및 도구 |
|-----------------|-----------------|-------------------|
| Victim PC       | 192.168.56.101  | `normal_status.py`, `safe_status.py` |
| Recursive DNS   | 192.168.56.102  | 취약 BIND9 (v9.4.2-P1), 포트 33333 |
| Attacker PC     | 192.168.56.103  | `attack.py`, Scapy |
| Authoritative DNS | 192.168.56.104 | `slow_dns.py`, dnslib 기반 응답 |

> 모든 VM은 VirtualBox Host-Only 네트워크에서 구성되어 있으며, 외부와 격리되어 있음.

---

### 🔹 공격 시나리오: Kaminsky Attack (CVE-2008-1447)

1. Victim이 `rand9999.netsec.kr`에 대한 DNS 질의 실행.
2. Authoritative DNS 서버의 응답 지연(6초) 사이에 Attacker가 forged response를 대량 전송.
3. Recursive DNS가 forged 응답을 먼저 수용하여 Cache 오염.
4. Victim은 공격자가 삽입한 IP(예: `1.1.1.1`)를 받게 됨.

---

### 🔹 방어 모델: Lightweight 해시 기반 인증

- 클라이언트 질의는 `nonce.hash.domain` 구조.
- Authoritative DNS는 전달된 `nonce + domain`을 기반으로 해시를 재계산하여 유효성 검증.
- 일치하지 않을 경우 NXDOMAIN 반환.
- TTL은 3초로 설정, Slow Resolver로 공격 타이밍 무력화.

---

## 🔐 보안 분석

### ✅ 공격자가 만족해야 할 조건:

1. **TXID** (16bit) 맞추기  
2. **Nonce** (랜덤 8자리) 맞추기  
3. **Hash 값** (SHA-256 → base64 상위 10자리) 맞추기

> 🔒 성공 확률은 극도로 낮음 (약 2^-118 수준)  
> 💡 UDP 포트 무작위화까지 적용하면 보안성은 2^16배 강화됨.

---

## 🧠 팀원 소감

### 🎙️ 이재현
> 단순 공격 구현을 넘어, DNS 프로토콜 흐름을 이해하고 실험적으로 검증하는 귀중한 경험. GPT의 도움으로 `tcpdump` 분석법을 익히며 실전 감각을 길렀음.

### 🎙️ 양동현
> 단일 공격 성공 확률을 수학적으로 분석하면서 보안 설계의 수리적 근거까지 고민. 실험 설계 및 실패 경험에서 실제 시스템 보안의 복잡성을 체감.

---

## 📚 참고자료

- [CVE-2008-1447 상세정보 (NVD)](https://nvd.nist.gov/vuln/detail/CVE-2008-1447)
- [dnslib 공식 문서](https://pypi.org/project/dnslib/)
- [Scapy 공식 문서](https://scapy.readthedocs.io/en/latest/)
- [Cloudflare - DNS Cache Poisoning 설명](https://www.cloudflare.com/ko-kr/learning/dns/dns-cache-poisoning/)

---

## 🏁 실행 방법 (예시)

```bash
# Victim PC에서 정상 요청 실행
$ python3 normal_status.py

# Attacker PC에서 공격 실행
$ python3 attack.py

# Victim PC에서 공격 여부 모니터링
$ dig rand9999.netsec.kr @192.168.56.102 -p 33333

# 방어 적용 후 안전한 요청
$ python3 safe_status.py

---
## 🔄 향후 개선 방향
- 실제 운영 환경에 맞춘 UDP 포트 무작위화 적용
- DNSSEC 등 표준 보안 프로토콜과의 통합 검증
- IDS와 연계한 공격 탐지 시스템 구축
---
