import requests
import json

import time

from datetime import date, timedelta
# 전역 파일 접근
import os
from dotenv import load_dotenv

# .env 파일에서 토큰 및 계정 정보 로드
load_dotenv(override=True)



my_token = os.getenv("ACCESS_TOKEN")
my_acc_id = os.getenv("ACT_ID")  # 예: 'act_1234567890'
my_app_id = os.getenv("APP_ID")
my_version = os.getenv("VERSION")
BASE_URL = f"https://graph.facebook.com/{my_version}"


# 조회할 데이터의 기간 정보
today = date.today()

# insights = 'campaign_name,adset_name,ad_name,impressions,clicks,reach,spend,conversions,conversion_values'
insights = "ad_name,impressions,clicks,ctr,cpc,spend,actions,action_values"


# ✅ 1. 광고 전체 목록 가져오기

ads_url = f"{BASE_URL}/{my_acc_id}/ads"
ads_params = {
    "fields": "id,name,status,creative",
    "access_token": my_token
}

ads_response = requests.get(ads_url, params=ads_params).json()
ads_data = ads_response.get("data", [])

print(f"📦 총 {len(ads_data)}개의 광고에서 성과 조회 시작...\n")

# 날짜 범위 지정
time_range = {
    "since": "2024-11-06",
    "until": "2024-11-06"
}

# 광고별 insights 조회
for ad in ads_data:
    ad_id = ad.get("id")
    ad_name = ad.get("name")
    creative_id = ad.get("creative", {}).get("id")


    insights_url = f"{BASE_URL}/{ad_id}/insights"
    insights_params = {
        "access_token": my_token,
        "fields": "impressions,clicks,reach,spend",
        "time_range": time_range
    }

    insights_res = requests.get(insights_url, params=insights_params).json()
    insights_data = insights_res.get("data", [])

    print(f"📣 광고: {ad_name} (ID: {ad_id})")
    
    if insights_data:
        insight = insights_data[0]
        print(f"   📊 노출 수(impressions): {insight.get('impressions', 0)}")
        print(f"   📊 클릭 수(clicks): {insight.get('clicks', 0)}")
        print(f"   📊 도달 수(reach): {insight.get('reach', 0)}")
        print(f"   💸 광고비(spend): {insight.get('spend', 0)}")
    else:
        print("   ⚠️ 성과 데이터 없음 (해당 기간 내 활동 없거나 결과 없음)")
    print("-" * 50)

    # 2. 크리에이티브 이미지/썸네일 조회
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
    print(f"   🖼️ 썸네일 URL: {thumbnail_url}")
