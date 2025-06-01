import requests
import json
import os
import time
from datetime import date
from io import BytesIO
from PIL import Image
import pandas as pd
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils.dataframe import dataframe_to_rows
from dotenv import load_dotenv

# Load .env
load_dotenv(override=True)

# 환경 변수
my_token = os.getenv("ACCESS_TOKEN")
my_acc_id = os.getenv("ACT_ID")
my_version = os.getenv("VERSION")
BASE_URL = f"https://graph.facebook.com/{my_version}"

# 날짜
time_range = {
    "since": "2024-11-06",
    "until": "2024-11-06"
}

# 결과 저장용 리스트
results = []

# 광고 목록
ads_url = f"{BASE_URL}/{my_acc_id}/ads"
ads_params = {
    "fields": "id,name,status,creative",
    "access_token": my_token
}
ads_response = requests.get(ads_url, params=ads_params).json()
ads_data = ads_response.get("data", [])

print(f"📦 총 {len(ads_data)}개의 광고에서 성과 조회 시작...\n")

# 이미지 저장용 딕셔너리
image_dict = {}

# 광고별 데이터 수집
for ad in ads_data:
    ad_id = ad.get("id")
    ad_name = ad.get("name", "-")
    creative_id = ad.get("creative", {}).get("id")

    # 성과 데이터 조회
    insights_url = f"{BASE_URL}/{ad_id}/insights"
    insights_params = {
        "access_token": my_token,
        "fields": "impressions,clicks,reach,spend",
        "time_range": time_range
    }

    insights_res = requests.get(insights_url, params=insights_params).json()
    insights_data = insights_res.get("data", [])

    if insights_data:
        insight = insights_data[0]
        impressions = insight.get("impressions", "-")
        clicks = insight.get("clicks", "-")
        reach = insight.get("reach", "-")
        spend = insight.get("spend", "-")
    else:
        impressions = clicks = reach = spend = "-"

    # 크리에이티브 이미지 URL 조회
    thumbnail_url = "N/A"
    if creative_id:
        creative_url = f"{BASE_URL}/{creative_id}"
        creative_params = {
            "fields": "image_url,thumbnail_url,object_story_spec",
            "access_token": my_token
        }
        creative_res = requests.get(creative_url, params=creative_params).json()

        thumbnail_url = (
            creative_res.get("image_url")
            or creative_res.get("thumbnail_url")
            or creative_res.get("object_story_spec", {}).get("video_data", {}).get("thumbnail_url")
            or "N/A"
        )

    # 이미지 다운로드 및 저장
    image = None
    if thumbnail_url.startswith("http"):
        try:
            img_data = requests.get(thumbnail_url).content
            image = Image.open(BytesIO(img_data))
            image_dict[ad_id] = image
        except:
            image = None

    results.append({
        "Ad Name": ad_name,
        "Ad ID": ad_id,
        "Impressions": impressions,
        "Clicks": clicks,
        "Reach": reach,
        "Spend": spend,
        "Image URL": thumbnail_url  # 참고용 URL
    })

# DataFrame 생성
df = pd.DataFrame(results)

# 엑셀 파일 생성
wb = Workbook()
ws = wb.active
ws.title = "Ad Insights"

# DataFrame을 엑셀로 쓰기
for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)

# 이미지 삽입
for row_idx, ad in enumerate(results, start=2):  # 1행은 헤더
    ad_id = ad["Ad ID"]
    if ad_id in image_dict:
        image = image_dict[ad_id]
        img_path = f"temp_{ad_id}.png"
        image.thumbnail((100, 100))  # 크기 조절
        image.save(img_path)
        img = XLImage(img_path)
        img.width, img.height = 80, 80
        ws.add_image(img, f"H{row_idx}")  # H 열 (Image URL 대신)
        os.remove(img_path)

# 엑셀 저장
output_dir = os.path.join(os.getcwd(), "data")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "facebook_ad_insights.xlsx")
wb.save(save_path)
print(f"✅ 엑셀 저장 완료: {save_path}")