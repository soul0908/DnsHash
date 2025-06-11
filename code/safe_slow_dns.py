import time
from dnslib import RR, QTYPE, A
from dnslib.server import DNSServer, BaseResolver
import hashlib
import base64

# 응답에 사용할 서버의 실제 IP
SERVER_IP = "192.168.56.104"

# domain + nonce를 결합해 SHA-256 해시 후 base64 인코딩 → 상위 10자리 사용
def generate_simple_hash(domain, nonce):
    combined = f"{domain}{nonce}".encode()
    sha = hashlib.sha256(combined).digest()
    return base64.urlsafe_b64encode(sha)[:10].decode()

# 커스텀 DNS 리졸버 클래스 정의
class SlowResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip('.')
        print(f"[DEBUG] Received query: {qname}")

        parts = qname.split('.')

        # 질의 형식 검사: 최소한 nonce.hash.domain 구조여야 함
        if len(parts) < 3:
            print("[WARN] Invalid query format.")
            return self.nxdomain_reply(request)

        # 쿼리에서 nonce, hash, domain 추출
        nonce, received_hash, domain = parts[0], parts[1], '.'.join(parts[2:])

        # 예상 해시값 계산
        expected_hash = generate_simple_hash(domain, nonce)

        print(f"[DEBUG] Nonce: {nonce}")
        print(f"[DEBUG] Received Hash: {received_hash}")
        print(f"[DEBUG] Expected Hash: {expected_hash}")

        # 해시값 일치 → 정상이므로 응답 반환
        if received_hash == expected_hash:
            reply = request.reply()
            reply.add_answer(RR(
                rname=request.q.qname,
                rtype=QTYPE.A,
                rclass=1,
                rdata=A(SERVER_IP),
                ttl=3
            ))
            time.sleep(1)  # 응답 지연 (slow resolver 역할)
            return reply

        # 해시값 불일치 → NXDOMAIN 반환
        else:
            print("return NXDOMAIN")
            return self.nxdomain_reply(request)

# DNS 서버 실행
if __name__ == "__main__":
    resolver = SlowResolver()
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    print("[AUTH] Lightweight DNS Server Running on 0.0.0.0:53")
    server.start()
