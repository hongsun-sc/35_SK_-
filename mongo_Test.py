from pymongo import MongoClient

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")

# 데이터베이스 선택
db = client["security_project"]

# 컬렉션 선택
collection = db["domains"]

print("MongoDB 연결 성공")
print("데이터베이스:", db.name)
print("컬렉션:", collection.name)

# 연결 확인
print("현재 저장된 데이터 수:", collection.count_documents({}))

client.close()