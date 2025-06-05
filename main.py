import requests
import os
import re
from dotenv import load_dotenv

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

# 광고 목록 조회
ads_url = f"{BASE_URL}/{my_acc_id}/ads"
ads_params = {
    "fields": "id,name,creative",
    "access_token": my_token,
    "time_range": {
    "since": "2025-05-06",
    "until": "2025-06-06"
}
}
ads_response = requests.get(ads_url, params=ads_params).json()
ads_data = ads_response.get("data", [])

print(f"📦 총 {len(ads_data)}개의 광고 이미지 저장 시작...\n")

for ad in ads_data:
    ad_id = ad.get("id")
    ad_name = ad.get("name")
    creative_id = ad.get("creative", {}).get("id")

    # 썸네일 URL 추출
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

    print(f"📣 광고: {ad_name}")
    print(f"🖼️ 썸네일 URL: {thumbnail_url}")

    # 이미지 저장
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
        print(ad_name, "⚠️ 썸네일 URL이 없어 이미지 저장 생략")

    print("-" * 50)
