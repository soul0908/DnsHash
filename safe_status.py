import hashlib
import base64
import random
from scapy.all import *

# 실험 대상 도메인, Recursive DNS 서버 IP, 포트
TARGET_DOMAIN = 'rand9999.netsec.kr'
RESOLVER_IP = '192.168.56.102'
RESOLVER_PORT = 33333
NONCE_LENGTH = 8

# 랜덤한 nonce 생성 함수
def generate_nonce(length=NONCE_LENGTH):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(length))

# (도메인 + nonce) 기반 SHA-256 해시 생성 후 base64 인코딩
def generate_simple_hash(domain, nonce):
    combined = f"{domain}{nonce}".encode()
    sha = hashlib.sha256(combined).digest()
    return base64.urlsafe_b64encode(sha)[:10].decode()

# DNS 질의 전송 및 응답 처리 함수
def send_query():
    nonce = generate_nonce()
    simple_hash = generate_simple_hash(TARGET_DOMAIN, nonce)
    qname_with_hash = f"{nonce}.{simple_hash}.{TARGET_DOMAIN}"

    print(f"[DEBUG] Nonce: {nonce}")
    print(f"[DEBUG] Generated Hash: {simple_hash}")
    print(f"[DEBUG] Full Qname: {qname_with_hash}")

    dns_request = IP(dst=RESOLVER_IP) / UDP(dport=RESOLVER_PORT) / DNS(rd=1, qd=DNSQR(qname=qname_with_hash))
    print(f"[INFO] Sending query: {qname_with_hash}")
    response = sr1(dns_request, verbose=0, timeout=2)

    if response and response.haslayer(DNS):
        response_qname = str(response[DNS].qd.qname.decode()).rstrip('.')
        resp_nonce, resp_hash, resp_domain = response_qname.split('.', 2)

        print(f"[DEBUG] Response Nonce: {resp_nonce}")
        print(f"[DEBUG] Response Hash: {resp_hash}")

        if resp_nonce == nonce and resp_hash == simple_hash:
            print(f"[PASS] Verified response. Nonce and hash match")
        else:
            print(f"[FAIL] Mismatch detected! Possible poisoning. Response nonce/hash do not match sent values.")
    else:
        print(f"[WARN] No response received.")

# 프로그램 실행 진입점
if __name__ == "__main__":
    send_query()
