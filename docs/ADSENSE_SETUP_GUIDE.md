# Google AdSense ads.txt 설정 가이드

**목적:** en.sedaily.com에서 Google AdSense 광고 수익화
**대상:** sedaily.com 도메인 관리자
**작업 시간:** 5분

---

## 1. ads.txt 파일이란?

**정의:**
- Authorized Digital Sellers (승인된 디지털 판매자)의 약자
- 광고 사기 방지를 위한 IAB 표준
- Google, 모든 주요 광고 플랫폼이 권장

**작동 원리:**
```
Google 광고 시스템
    ↓
sedaily.com/ads.txt 파일 확인
    ↓
승인된 계정(pub-1326078912759552) 확인
    ↓
en.sedaily.com에 광고 게재 허용
```

---

## 2. 설정 방법

### 옵션 A: 기존 ads.txt 파일이 있는 경우

**1단계: 기존 파일 열기**
```
https://sedaily.com/ads.txt
```

**2단계: 맨 아래에 1줄 추가**
```
google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0
```

**3단계: 저장**

---

### 옵션 B: ads.txt 파일이 없는 경우

**1단계: 텍스트 파일 생성**
- 파일명: `ads.txt`
- 인코딩: UTF-8
- 확장자: .txt (중요!)

**2단계: 내용 입력**
```
google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0
```

**3단계: 웹 서버 루트에 업로드**
```
/var/www/html/ads.txt
또는
/public_html/ads.txt
```

**4단계: 접근 권한 확인**
```bash
# 파일 권한 (644 권장)
chmod 644 ads.txt

# Content-Type 확인 (text/plain 이어야 함)
curl -I https://sedaily.com/ads.txt
```

---

## 3. 각 항목 설명

```
google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0
```

| 항목 | 값 | 설명 |
|------|-----|------|
| **도메인** | `google.com` | 광고 시스템 (Google AdSense) |
| **퍼블리셔 ID** | `pub-1326078912759552` | en.sedaily.com의 AdSense 계정 ID |
| **관계** | `DIRECT` | 직접 관계 (중개 없음) |
| **인증 ID** | `f08c47fec0942fa0` | Google의 공식 인증 ID |

---

## 4. 검증 방법

### 브라우저 확인
```
https://sedaily.com/ads.txt
```

**정상 출력 예:**
```
google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0
```

### Google 검증 도구
```
https://adstxt.guru/sedaily.com
```

**예상 결과:**
```
✅ ads.txt found
✅ Google AdSense: pub-1326078912759552 (DIRECT)
✅ No errors
```

---

## 5. 주의사항

### ✅ 해야 할 것

1. **파일명 정확히:** `ads.txt` (소문자)
2. **루트 경로:** https://sedaily.com/ads.txt
3. **텍스트 형식:** plain text (HTML 아님)
4. **줄바꿈:** Unix 스타일 (LF)

### ❌ 하지 말아야 할 것

1. **잘못된 경로:**
   - ❌ https://sedaily.com/assets/ads.txt
   - ❌ https://www.sedaily.com/ads.txt (www 붙이면 안됨)
   - ✅ https://sedaily.com/ads.txt (정확한 경로)

2. **잘못된 형식:**
   - ❌ ads.html
   - ❌ ads.txt.txt
   - ✅ ads.txt

3. **공백 추가:**
   - ❌ google.com ,  pub-1326078912759552, DIRECT, f08c47fec0942fa0
   - ✅ google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0

---

## 6. 서버별 설정 방법

### Apache 서버

**위치:**
```
/var/www/html/ads.txt
```

**업로드:**
```bash
# FTP/SFTP로 업로드 또는
sudo nano /var/www/html/ads.txt
# 내용 입력 후 저장 (Ctrl+O, Ctrl+X)
```

**.htaccess (선택사항 - Content-Type 명시):**
```apache
<Files "ads.txt">
    ForceType text/plain
    Header set Access-Control-Allow-Origin "*"
</Files>
```

---

### Nginx 서버

**위치:**
```
/usr/share/nginx/html/ads.txt
또는
/var/www/sedaily.com/ads.txt
```

**nginx.conf 설정 (선택사항):**
```nginx
location = /ads.txt {
    add_header Content-Type text/plain;
    add_header Access-Control-Allow-Origin *;
}
```

---

### WordPress

**방법 1: FTP 업로드**
```
/public_html/ads.txt
```

**방법 2: 플러그인 사용**
- Plugin: "Ads.txt Manager" by 10up
- Settings → Ads.txt → 내용 입력 → 저장

---

### CDN (CloudFront, Cloudflare)

**중요:** ads.txt는 CDN 캐싱 **제외** 설정 필요

**CloudFront:**
```json
{
  "PathPattern": "/ads.txt",
  "MinTTL": 0,
  "DefaultTTL": 0,
  "MaxTTL": 0
}
```

**Cloudflare Page Rules:**
```
https://sedaily.com/ads.txt
Cache Level: Bypass
```

---

## 7. 트러블슈팅

### 문제 1: ads.txt를 찾을 수 없음 (404)

**원인:**
- 파일이 루트 경로에 없음
- 파일명 오타

**해결:**
```bash
# 현재 위치 확인
pwd

# 파일 존재 확인
ls -la ads.txt

# 루트로 이동 후 업로드
cd /var/www/html
```

---

### 문제 2: Content-Type이 잘못됨

**증상:**
```
Content-Type: text/html
```

**해결:**
```bash
# .htaccess에 추가 (Apache)
<Files "ads.txt">
    ForceType text/plain
</Files>

# nginx.conf에 추가 (Nginx)
location = /ads.txt {
    add_header Content-Type text/plain;
}
```

---

### 문제 3: Google이 인식하지 못함

**확인 사항:**
1. https://sedaily.com/ads.txt 브라우저 접속 확인
2. pub-1326078912759552 ID 정확히 입력되었는지
3. 24-48시간 대기 (Google 크롤러 재방문 시간)

---

## 8. 완료 후 확인

### 1단계: 브라우저 확인
```
https://sedaily.com/ads.txt
```

### 2단계: curl 확인
```bash
curl -I https://sedaily.com/ads.txt

# 예상 출력:
HTTP/2 200
content-type: text/plain
```

### 3단계: Google AdSense 확인
```
1. Google AdSense 계정 로그인
2. Sites → sedaily.com 확인
3. "ads.txt 파일 발견됨" 메시지 확인
```

---

## 9. FAQ

**Q: en.sedaily.com에도 ads.txt를 추가해야 하나요?**
A: 아니요. 루트 도메인(sedaily.com)에만 추가하면 모든 서브도메인에 자동 적용됩니다.

**Q: 기존 ads.txt에 다른 내용이 있는데 어떻게 하나요?**
A: 기존 내용 아래에 새 줄을 추가하면 됩니다. 여러 줄 가능합니다.

**Q: sedaily.com에 영향이 있나요?**
A: 없습니다. en.sedaily.com 전용 설정입니다.

**Q: 언제부터 광고가 나오나요?**
A: ads.txt 설정 후 Google 검증 완료까지 24-48시간 소요됩니다.

---

## 10. 연락처

설정 중 문제가 있으시면 연락 주세요:

**담당자:** [귀하의 이름]
**이메일:** [이메일]
**전화:** [전화번호]

---

**작성일:** 2026-01-02
**문서 버전:** 1.0
