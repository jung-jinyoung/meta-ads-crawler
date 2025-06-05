Meta (Facebook) Graph API를 활용해 광고 목록을 조회하고, 각 광고의 썸네일 이미지를 자동으로 다운로드하는 Python 스크립트입니다.

## 1. `.env` 파일 생성

먼저, API 호출에 필요한 인증 정보를 담은 `.env` 파일을 프로젝트 루트 디렉토리에 생성하세요.

```python
ACCESS_TOKEN=your-facebook-access-token
ACT_ID=act_1234567890         # act+광고 계정 ID
VERSION=v22.0
```

> `.env` 파일 내에서는 `=` 기호 **좌우에 절대 띄어쓰기를 넣지 마세요.**
>
> 예) `ACCESS_TOKEN = your_token` ❌ → `ACCESS_TOKEN=your_token` ✅

> `ACT_ID`에는 반드시 **`act_` 접두어를 포함한 광고 계정 ID**를 입력해야 합니다.
>
> 예) `ACT_ID=act_1234567890`

> `ACCESS_TOKEN`은 **Meta for Developers**에서 발급한 유효한 사용자 액세스 토큰이어야 하며,
>
> 만료 시 다시 발급받아야 합니다.

### Token, ID 관련 페이지

1. access_token, app-id 발급 및 조회 관련 참고 페이지

   https://milkyspace.tistory.com/122

2. access_token 만료 기한 연장 관련 참고 페이지

   https://onee95.tistory.com/entry/Meta-%EB%A7%88%EC%BC%80%ED%8C%85-API%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%EA%B4%91%EA%B3%A0-%EB%A6%AC%ED%8F%AC%ED%8C%85-1

## 2. 필요 라이브러리 설치

아래 명령어를 통해 필요한 파이썬 패키지를 설치하세요:

```bash
pip install requests python-dotenv
```

## 3. 코드 설명

1. `.env`에서 환경 변수 로드
2. 광고 목록 요청 → 각 광고의 creative ID 확보
3. 이미지 URL 추출 → 이미지 다운로드
4. 썸네일 이미지를 `./data/` 폴더에 광고 이름으로 저장

---

### 🗓️ 날짜 설정 방법

이 스크립트는 **특정 기간 동안 활동한 광고의 썸네일만 저장**합니다.

```python
"since": "2025-05-06",  # 시작일
"until": "2025-06-06"   # 종료일
```

해당 기간 내에 광고가 **활동한 적이 있는 경우에만** 이미지가 다운로드됩니다.

> 필요 시 Python datetime 모듈로 동적으로 날짜 설정도 가능합니다.

### 💾 이미지 저장 관련 설정

- 저장 폴더: `./data/`
- 저장 파일명: 광고 이름 (`광고이름.jpg`)
- 파일명에 허용되지 않는 문자는 자동으로 `_`로 치환됩니다.

> 폴더명을 변경을 원할 경우 코드 내에서 변경하면 됩니다.
>
> ```bash
> # 저장할 폴더 경로
> SAVE_DIR = "./data" # <- 해당 폴더명을 변경
> os.makedirs(SAVE_DIR, exist_ok=True)
> ```

### 🔒 안전한 이미지 다운로드 처리

- `requests.get(..., stream=True)` + `with` 문을 사용하여 리소스 누수를 방지합니다.
- 이미지 다운로드 중 오류 발생 시 해당 항목은 건너뜁니다.

## 4. 실행 방법

```bash
python main.py
```

> 다운로드된 이미지 파일은 ./data/ 폴더에서 확인할 수 있습니다. (폴더명을 변경했을 경우 해당 폴더에서 확인 가능)

## 참고

- Meta API를 통해 `creative.image_url` 또는 `object_story_spec.video_data.thumbnail_url`을 참조하여 이미지 URL을 가져옵니다.
- 이미지가 없는 광고는 자동으로 건너뜁니다.
