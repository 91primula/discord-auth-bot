# 베이스 이미지 (Python 3.11)
FROM python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 환경 변수는 Koyeb Dashboard에서 설정
CMD ["python", "bot.py"]
