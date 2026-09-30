import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient


# =========================================================
# 0. 환경 설정
# =========================================================

load_dotenv()

API_KEY = os.getenv("DATA_GO_KR_KEY")

if not API_KEY:
    print(".env에서 인증키를 불러오지 못했습니다.")
    exit()


url = "https://apis.data.go.kr/B551505/whois/domain_name"


# =========================================================
# 1. 도메인 목록 불러오기
# =========================================================

try:

    with open("domains.txt", "r", encoding="utf-8") as file:

        domains = [
            line.strip()
            for line in file
            if line.strip()
        ]

except FileNotFoundError:

    print("domains.txt 파일을 찾을 수 없습니다.")
    exit()


print("총 조회할 도메인:", len(domains))
print()


# =========================================================
# 2. 도메인 분류
# =========================================================

category_map = {

    # -----------------------------------------------------
    # 정부기관
    # -----------------------------------------------------

    "kisa.or.kr": "정부기관",
    "police.go.kr": "정부기관",
    "moj.go.kr": "정부기관",
    "mois.go.kr": "정부기관",
    "mofa.go.kr": "정부기관",
    "kostat.go.kr": "정부기관",

    "moel.go.kr": "정부기관",
    "msit.go.kr": "정부기관",
    "mss.go.kr": "정부기관",
    "mcst.go.kr": "정부기관",
    "mfds.go.kr": "정부기관",
    "nfa.go.kr": "정부기관",


    # -----------------------------------------------------
    # 공공기관 / 공공서비스
    # -----------------------------------------------------

    "korea.kr": "공공서비스",
    "data.go.kr": "공공서비스",
    "gov.kr": "공공서비스",
    "epeople.go.kr": "공공서비스",
    "alio.go.kr": "공공서비스",
    "kosis.kr": "공공서비스",
    "g2b.go.kr": "공공서비스",
    "work24.go.kr": "공공서비스",
    "wetax.go.kr": "공공서비스",
    "k-startup.go.kr": "공공서비스",


    # -----------------------------------------------------
    # 금융 / 경제
    # -----------------------------------------------------

    "bok.or.kr": "금융·경제",
    "fss.or.kr": "금융·경제",
    "fsc.go.kr": "금융·경제",
    "kfb.or.kr": "금융·경제",
    "koscom.co.kr": "금융·경제",


    # -----------------------------------------------------
    # 교육 / 연구
    # -----------------------------------------------------

    "snu.ac.kr": "교육·연구",
    "kaist.ac.kr": "교육·연구",
    "postech.ac.kr": "교육·연구",
    "yonsei.ac.kr": "교육·연구",
    "korea.ac.kr": "교육·연구",


    # -----------------------------------------------------
    # 기업
    # -----------------------------------------------------

    "samsung.co.kr": "기업",
    "lge.co.kr": "기업",
    "sk.co.kr": "기업",
    "lotte.co.kr": "기업",
    "cj.co.kr": "기업",
    "posco.co.kr": "기업",
    "hanwha.co.kr": "기업",
    "hyundai.co.kr": "기업",
    "nh.co.kr": "기업",
    "naver.co.kr": "기업"
}


# =========================================================
# 3. 날짜 변환 함수
# =========================================================

def convert_date(date_string):

    if not date_string:
        return None

    try:

        return datetime.strptime(
            date_string,
            "%Y. %m. %d."
        )

    except ValueError:

        return None


# =========================================================
# 4. API 데이터 수집
# =========================================================

results = []

failed_domains = []


for domain in domains:

    print("도메인:", domain)


    # -----------------------------------------------------
    # API 요청 파라미터
    # -----------------------------------------------------

    params = {

        "serviceKey": API_KEY,
        "query": domain,
        "answer": "json"

    }


    # -----------------------------------------------------
    # API 요청
    # -----------------------------------------------------

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

    except requests.RequestException as e:

        print("API 요청 오류:", e)

        failed_domains.append(domain)

        print("-" * 50)

        continue


    print("상태 코드:", response.status_code)


    # -----------------------------------------------------
    # HTTP 상태 코드 확인
    # -----------------------------------------------------

    if response.status_code != 200:

        print("API 요청 실패")
        print(response.text)

        failed_domains.append(domain)

        print("-" * 50)

        continue


    # -----------------------------------------------------
    # JSON 변환
    # -----------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        print("JSON 데이터를 읽을 수 없습니다.")

        failed_domains.append(domain)

        print("-" * 50)

        continue


    # -----------------------------------------------------
    # WHOIS 데이터 접근
    # -----------------------------------------------------

    response_data = data.get(
        "response",
        {}
    )

    whois_data = response_data.get(
        "whois",
        {}
    )

    whois = whois_data.get(
        "krdomain"
    )


    # -----------------------------------------------------
    # 도메인 정보 존재 여부 확인
    # -----------------------------------------------------

    if whois is None:

        print("도메인 정보를 찾을 수 없습니다.")

        failed_domains.append(domain)

        print("-" * 50)

        continue


    # =====================================================
    # 5. 필요한 데이터 추출
    # =====================================================

    registration_date = whois.get(
        "regDate"
    )

    expiration_date = whois.get(
        "endDate"
    )

    last_updated = whois.get(
        "lastUpdatedDate"
    )

    dnssec = whois.get(
        "dnssec"
    )

    domain_status = whois.get(
        "domainStatus"
    ) or []

    nameservers = whois.get(
        "ns"
    ) or []

    ips = whois.get(
        "ip"
    ) or []


    # =====================================================
    # 6. 날짜 전처리
    # =====================================================

    registration_date = convert_date(
        registration_date
    )

    expiration_date = convert_date(
        expiration_date
    )

    last_updated = convert_date(
        last_updated
    )


    # =====================================================
    # 7. IP 전처리
    # =====================================================

    ips = [

        ip
        for ip in ips
        if ip is not None

    ]


    # =====================================================
    # 8. 도메인 분류
    # =====================================================

    category = category_map.get(
        domain,
        "기타"
    )


    # =====================================================
    # 9. MongoDB 저장용 데이터 생성
    # =====================================================

    result = {

        "domain": domain,

        "category": category,

        "registration_date": registration_date,

        "expiration_date": expiration_date,

        "last_updated": last_updated,

        "dnssec": dnssec,

        "domain_status": domain_status,

        "nameservers": nameservers,

        "ips": ips,

        "nameserver_count": len(
            nameservers
        ),

        "ip_count": len(
            ips
        )

    }


    results.append(
        result
    )


    # =====================================================
    # 10. 수집 결과 출력
    # =====================================================

    print("수집 완료")

    print(
        "분류:",
        category
    )

    print(
        "DNSSEC:",
        dnssec
    )

    print(
        "네임서버 수:",
        len(nameservers)
    )

    print(
        "IP 수:",
        len(ips)
    )

    print("-" * 50)


# =========================================================
# 11. 최종 수집 결과
# =========================================================

print()
print("========================================")
print("최종 수집 결과")
print("========================================")

print(
    "전체 조회:",
    len(domains)
)

print(
    "성공:",
    len(results)
)

print(
    "실패:",
    len(failed_domains)
)


# =========================================================
# 12. 실패한 도메인 출력
# =========================================================

if failed_domains:

    print()
    print("===== 조회 실패 도메인 =====")

    for domain in failed_domains:

        print(domain)


# =========================================================
# 13. MongoDB 연결
# =========================================================

print()
print("========================================")
print("MongoDB 저장")
print("========================================")


client = MongoClient(
    "mongodb://localhost:27017/"
)


db = client[
    "security_project"
]


collection = db[
    "domains"
]


# =========================================================
# 14. MongoDB 저장
# =========================================================

# 기존 데이터 삭제
collection.delete_many({})

# 현재 수집한 데이터만 저장
if results:
    collection.insert_many(results)

saved_count = collection.count_documents({})
# =========================================================
# 15. 저장 결과 확인
# =========================================================

saved_count = collection.count_documents({})


print(
    "MongoDB 저장 완료:",
    saved_count
)


# =========================================================
# 16. 최종 요약
# =========================================================

print()
print("========================================")
print("프로그램 종료")
print("========================================")

print(
    "전체 도메인:",
    len(domains)
)

print(
    "성공:",
    len(results)
)

print(
    "실패:",
    len(failed_domains)
)

print(
    "MongoDB 전체 데이터:",
    saved_count
)


# =========================================================
# 17. MongoDB 연결 종료
# =========================================================

client.close()