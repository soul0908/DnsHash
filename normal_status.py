import subprocess
import time

# 질의할 도메인 이름
target_domain = "rand9999.netsec.kr"
# 예상되는 응답 IP (공격 성공 시 1.1.1.1로 바뀜)
expected_ip = "1.1.1.1"
# Recursive DNS 서버 IP
bind9_ip = "192.168.56.102"
# BIND9 DNS 서버 포트
bind9_port = "33333"
# 질의 주기 (초)
check_interval = 2

# dig 명령어를 실행해 DNS 응답을 확인하는 함수
def check_dns():
    try:
        result = subprocess.run(
            ["dig", f"@{bind9_ip}", "-p", bind9_port, target_domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        # 오류가 있으면 출력
        if stderr:
            print(f"[DIG ERROR] {stderr}")
        return stdout
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

# 메인 루프: 예상 IP가 응답될 때까지 반복 확인
if __name__ == "__main__":
    print(f"[INFO] {target_domain} to response {expected_ip}...")
    while True:
        answer = check_dns()
        print(f"[CHECK] full dig output :\n {answer}")
        # 예상 IP와 응답이 일치하면 성공 출력 후 종료
        if answer == expected_ip:
            print(f"[SUCCESS] success {target_domain} -> {expected_ip}")
            break
        # 주기적으로 다시 확인
        time.sleep(check_interval)
