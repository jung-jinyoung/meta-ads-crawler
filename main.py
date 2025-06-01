import requests
import time

from datetime import date, timedelta
# 전역 파일 접근
import os
from dotenv import load_dotenv

# .env 파일에서 토큰 및 계정 정보 로드
load_dotenv()



my_access_token = os.getenv("ACCESS_TOKEN")
my_ad_account_id = os.getenv("AD_ACCOUNT_ID")  # 예: 'act_1234567890'
my_version = os.getenv("VERSION")

# 조회할 데이터의 기간 정보
today = date.today()

# insights = 'campaign_name,adset_name,ad_name,impressions,clicks,reach,spend,conversions,conversion_values'
insights = "ad_name,impressions,clicks,ctr,cpc,spend,actions,action_values"

url = f"https://graph.facebook.com/{my_version}/{my_ad_account_id}/insights"
params = {
    'fields': insights,
    'use_unified_attribution_setting' : True,
    'level' : "ad",
    'access_token' : my_access_token
}

r = requests.get(url = url, params = params)

print(r.text)