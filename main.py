import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime


# 환경 변수 로드
load_dotenv(override=True)

my_token = os.getenv("ACCESS_TOKEN")
my_acc_id = os.getenv("ACT_ID")
my_version = os.getenv("VERSION")
BASE_URL = f"https://graph.facebook.com/{my_version}"

# 저장할 폴더 경로
SAVE_DIR = "./data"
os.makedirs(SAVE_DIR, exist_ok=True)

# 파일 이름 안전하게 변환
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

# 날짜 필터링
def is_date_in_range(start, end, filter_start, filter_end):
    fmt = "%Y-%m-%d"
    return datetime.strptime(end, fmt) >= datetime.strptime(filter_start, fmt) or \
           datetime.strptime(start, fmt) <= datetime.strptime(filter_end, fmt)

# 필터 기준 날짜 : yyyy-mm-dd
FILTER_START = "2025-05-09"
FILTER_END = "2025-06-07"

ads_url = (
    f"{BASE_URL}/{my_acc_id}/ads"
    "?fields=id,name,creative,configured_status,adset_id"
    "&configured_status=['ACTIVE']"
    f"&access_token={my_token}"
)

ads_response = requests.get(ads_url).json()
ads_data = ads_response.get("data", [])
print(f"📦 총 {len(ads_data)}개의 광고 이미지 필터링 시작...\n")

# 날짜 필터링 광고 데이터 리스트 초기화
filtered_ads = []

for ad in ads_data:
    ad_id = ad.get("id")
    ad_name = ad.get("name")
    adset_id = ad.get("adset_id")
    if not adset_id:
        continue

    # 광고셋의 기간 확인
    adset_url = f"{BASE_URL}/{adset_id}"
    adset_params = {
        "fields": "start_time,end_time",
        "access_token": my_token
    }
    adset_res = requests.get(adset_url, params=adset_params).json()
    start_time = adset_res.get("start_time", "")[:10]
    end_time = adset_res.get("end_time", "")[:10]
    print(ad_name, start_time, end_time)

    if start_time and end_time and is_date_in_range(start_time, end_time, FILTER_START, FILTER_END):
        ad["creative_id"] = ad.get("creative", {}).get("id")
        filtered_ads.append(ad)
    elif start_time and not end_time and is_date_in_range(start_time, start_time, FILTER_START, FILTER_END):
        ad["creative_id"] = ad.get("creative", {}).get("id")
        filtered_ads.append(ad)

print(f"📦 총 {len(filtered_ads)}개의 광고 이미지 저장 시작...\n")

# 이미지 저장
for ad in filtered_ads:
    ad_name = ad.get("name")
    creative_id = ad.get("creative_id")
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

    if thumbnail_url != "N/A":
        try:
            image_res = requests.get(thumbnail_url, stream=True)
            if image_res.status_code == 200:
                safe_ad_name = clean_filename(ad_name)
                file_path = os.path.join(SAVE_DIR, f"{safe_ad_name}.jpg")
                with open(file_path, "wb") as f:
                    for chunk in image_res.iter_content(1024):
                        f.write(chunk)
                print(f"✅ 이미지 저장 완료: {file_path}")
            else:
                print(f"❌ 이미지 다운로드 실패 (Status Code: {image_res.status_code})")
        except Exception as e:
            print(f"❌ 이미지 저장 중 오류 발생: {e}")
    else:
        print(f"⚠️ 썸네일 URL 없음 - 이미지 저장 생략")

    print("-" * 50)