from dnslib.server import DNSServer, DNSHandler, BaseResolver
from dnslib import RR, QTYPE, A
import dnslib
import time

# SlowResolver 클래스 정의 (응답을 의도적으로 지연)
class SlowResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname)
        qtype = QTYPE[request.q.qtype]

        print(f"Received query: {qname} ({qtype})")

        # 특정 도메인 질의만 응답 처리
        if qname.rstrip('.').endswith("rand9999.netsec.kr"):
            reply = request.reply()
            # A 레코드 응답 추가 (192.168.56.104로 응답)
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("192.168.56.104"), ttl=3))
            # 응답 지연 (6초)
            time.sleep(6)
            return reply

        # 나머지 질의는 NXDOMAIN으로 응답
        reply = request.reply()
        reply.header.rcode = getattr(dnslib.RCODE, 'NXDOMAIN')
        print(f"Received query: [{qname}] ({qtype})")
        return reply

# 서버 실행부
if __name__ == "__main__":
    resolver = SlowResolver()
    server = DNSServer(resolver, port=53, address="0.0.0.0")
    print("[AUTH] Slow DNS server running on 0.0.0.0:53")
    server.start()
