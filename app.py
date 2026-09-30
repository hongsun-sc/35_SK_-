from flask import Flask, render_template
from pymongo import MongoClient


# =========================================================
# 1. Flask 설정
# =========================================================

app = Flask(__name__)


# =========================================================
# 2. MongoDB 연결
# =========================================================

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["security_project"]

collection = db["domains"]


# =========================================================
# 3. 메인 페이지
# =========================================================

@app.route("/")
def index():

    # -----------------------------------------------------
    # MongoDB 데이터 가져오기
    # -----------------------------------------------------

    domains = list(
        collection.find(
            {},
            {
                "_id": 0
            }
        )
    )


    # =====================================================
    # 4. 전체 도메인 수
    # =====================================================

    total_domains = len(domains)


    # =====================================================
    # 5. 카테고리별 도메인 수
    # =====================================================

    category_counts = {}

    for domain in domains:

        category = domain.get(
            "category",
            "기타"
        )

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )


    # =====================================================
    # 6. DNSSEC 현황
    # =====================================================

    dnssec_counts = {
        "signed": 0,
        "unsigned": 0
    }

    for domain in domains:

        dnssec = domain.get("dnssec")

        if dnssec == "signed":

            dnssec_counts["signed"] += 1

        else:

            dnssec_counts["unsigned"] += 1


    # =====================================================
    # 7. 평균 네임서버 수
    # =====================================================

    if total_domains > 0:

        avg_nameservers = round(

            sum(
                domain.get(
                    "nameserver_count",
                    0
                )
                for domain in domains
            )
            / total_domains,

            2
        )

    else:

        avg_nameservers = 0


    # =====================================================
    # 8. 평균 IP 수
    # =====================================================

    if total_domains > 0:

        avg_ips = round(

            sum(
                domain.get(
                    "ip_count",
                    0
                )
                for domain in domains
            )
            / total_domains,

            2
        )

    else:

        avg_ips = 0


    # =====================================================
    # 9. 카테고리별 평균 네임서버 수
    # =====================================================

    category_nameserver_sum = {}

    category_nameserver_count = {}


    for domain in domains:

        category = domain.get(
            "category",
            "기타"
        )

        nameserver_count = domain.get(
            "nameserver_count",
            0
        )


        category_nameserver_sum[category] = (

            category_nameserver_sum.get(
                category,
                0
            )
            + nameserver_count

        )


        category_nameserver_count[category] = (

            category_nameserver_count.get(
                category,
                0
            )
            + 1

        )


    category_avg_nameservers = {}


    for category in category_nameserver_sum:

        category_avg_nameservers[category] = round(

            category_nameserver_sum[category]
            / category_nameserver_count[category],

            2

        )


    # =====================================================
    # 10. 등록 연도별 도메인 수
    # =====================================================

    registration_year_counts = {}


    for domain in domains:

        registration_date = domain.get(
            "registration_date"
        )


        if registration_date:

            year = registration_date.year

            registration_year_counts[year] = (

                registration_year_counts.get(
                    year,
                    0
                )
                + 1

            )


    # 연도 순서대로 정렬

    registration_year_counts = dict(
        sorted(
            registration_year_counts.items()
        )
    )


    # =====================================================
    # 11. 네임서버 수 TOP 10
    # =====================================================

    top_nameservers = sorted(

        domains,

        key=lambda x: x.get(
            "nameserver_count",
            0
        ),

        reverse=True

    )[:10]


    # =====================================================
    # 12. IP 수 TOP 10
    # =====================================================

    top_ips = sorted(

        domains,

        key=lambda x: x.get(
            "ip_count",
            0
        ),

        reverse=True

    )[:10]


    # =====================================================
    # 13. HTML로 데이터 전달
    # =====================================================

    return render_template(

        "index.html",

        domains=domains,

        total_domains=total_domains,

        category_counts=category_counts,

        dnssec_counts=dnssec_counts,

        avg_nameservers=avg_nameservers,

        avg_ips=avg_ips,

        category_avg_nameservers=category_avg_nameservers,

        registration_year_counts=registration_year_counts,

        top_nameservers=top_nameservers,

        top_ips=top_ips

    )


# =========================================================
# 14. Flask 실행
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )