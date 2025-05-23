# ベースイメージ
FROM python:3.12

# 作業ディレクトリを設定
WORKDIR /code

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-jpn
