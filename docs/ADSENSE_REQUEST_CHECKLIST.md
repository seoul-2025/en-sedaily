# Google AdSense 협조 요청 체크리스트

## 준비 자료 ✅

### 1. 이메일 전송
- [ ] 요청 메일 작성 (템플릿 사용)
- [ ] ADSENSE_SETUP_GUIDE.md 첨부
- [ ] ads.txt 파일 첨부
- [ ] 담당자 확인 (IT팀/웹마스터)

### 2. 첨부 파일
- [ ] `ADSENSE_SETUP_GUIDE.md` - 설정 가이드
- [ ] `ads.txt` - 업로드할 파일

### 3. 요청 내용 확인
- [ ] 파일 위치: `https://sedaily.com/ads.txt`
- [ ] 파일 내용: `google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0`
- [ ] 예상 소요 시간: 5분
- [ ] 예상 효과: en.sedaily.com AdSense 활성화

---

## 협조 요청 순서

### 📧 Step 1: 담당자 파악 (D-Day)

**확인 사항:**
- [ ] sedaily.com 웹마스터가 누구인가?
- [ ] IT팀 담당자 이메일
- [ ] 승인 라인 (팀장/부장 등)

**예상 담당 부서:**
- IT개발팀
- 디지털미디어팀
- 웹서비스팀

---

### 📨 Step 2: 공식 요청 메일 발송 (D+1)

**수신:**
- IT팀 담당자
- 참조: 상위 결재자

**제목:**
```
[요청] en.sedaily.com Google AdSense 연동을 위한 ads.txt 파일 추가
```

**첨부:**
1. ADSENSE_SETUP_GUIDE.md
2. ads.txt

---

### 📞 Step 3: 후속 조치 (D+2-3)

**회신 없을 시:**
- [ ] 전화 확인
- [ ] 대면 미팅 요청
- [ ] 간단한 슬랙/카톡 메시지

**회신 있을 시:**
- [ ] 작업 일정 확인
- [ ] 추가 질문 답변
- [ ] 설정 지원 제안

---

### ✅ Step 4: 설정 완료 확인 (D+7)

**확인 항목:**
```bash
# 1. 브라우저 확인
https://sedaily.com/ads.txt

# 2. curl 확인
curl https://sedaily.com/ads.txt

# 예상 출력:
google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0
```

**Google 검증:**
- [ ] https://adstxt.guru/sedaily.com 확인
- [ ] Google AdSense 계정에서 "ads.txt 발견" 확인

---

### 🎉 Step 5: AdSense 승인 신청 (D+8-9)

**Google AdSense 계정:**
1. Sites → Add site
2. `en.sedaily.com` 입력
3. 코드 삽입 확인 (이미 완료됨)
4. 승인 대기 (1-2주)

---

## 예상 타임라인

| 일정 | 작업 | 담당 | 상태 |
|------|------|------|------|
| D-Day | 담당자 파악 | 본인 | ⬜ |
| D+1 | 요청 메일 발송 | 본인 | ⬜ |
| D+2-3 | 후속 연락 | 본인 | ⬜ |
| D+5-7 | ads.txt 설정 | IT팀 | ⬜ |
| D+7 | 설정 확인 | 본인 | ⬜ |
| D+8-9 | AdSense 승인 신청 | 본인 | ⬜ |
| D+22-30 | AdSense 승인 완료 | Google | ⬜ |

---

## 예상 질문 & 답변

### Q1: "왜 sedaily.com에 설정해야 하나요?"
**A:** Google AdSense는 서브도메인의 경우 루트 도메인에서 승인 확인을 합니다.
en.sedaily.com은 sedaily.com의 서브도메인이므로, 루트에 ads.txt가 필요합니다.

---

### Q2: "sedaily.com 본사 사이트에 영향은 없나요?"
**A:** 전혀 없습니다.
- 파일은 텍스트 70바이트
- 본사 사이트 성능/기능에 0% 영향
- en.sedaily.com 전용 설정입니다

---

### Q3: "작업 시간이 얼마나 걸리나요?"
**A:** 약 5분입니다.
1. ads.txt 파일 업로드 (2분)
2. 브라우저 확인 (1분)
3. 보고서 작성 (2분)

---

### Q4: "보안 문제는 없나요?"
**A:** 전혀 없습니다.
- ads.txt는 IAB(Interactive Advertising Bureau) 표준
- Google, Facebook, Amazon 등 모든 광고 플랫폼이 사용
- 전 세계 수백만 사이트가 사용 중

---

### Q5: "나중에 수정이 필요한가요?"
**A:** 아니요, 한 번 설정하면 끝입니다.
- AdSense 계정 ID는 변경되지 않음
- 추가 광고 플랫폼 사용 시에만 줄 추가

---

## 설득 포인트

### 💰 수익화
- 현재 en.sedaily.com 월 방문자: 증가 중
- 예상 월 광고 수익: $500-2,000
- 연간 예상: $6,000-24,000

### 📊 데이터
- Google Search Console: 361,604 impressions
- GA4: 1,423 users (3일간)
- AI 검색 트래픽: 49% (ChatGPT #1)

### 🚀 성장 가능성
- SEO 순위 개선: 24.4 → 5.6 (78%)
- 200개국 도달
- 비용 없이 수익 창출 가능

---

## 백업 플랜

### 협조 거부 시:

**Plan B: DNS TXT 레코드**
- sedaily.com DNS 관리자에게 요청
- TXT 레코드 추가로도 가능 (더 복잡함)

**Plan C: 상위 결재자 승인**
- 경제적 효과 강조
- 수익 분석 자료 제출
- 회의 요청

---

## 연락 템플릿

### 후속 연락 (전화/카톡)

```
안녕하세요, [이름]입니다.

어제 메일로 요청드린 en.sedaily.com AdSense 설정 건
확인하셨는지 궁금해서 연락드렸습니다.

간단한 텍스트 파일 업로드로 5분이면 완료되는 작업인데,
혹시 제가 직접 도와드릴까요?

시간 되실 때 답변 부탁드립니다!
```

---

## 완료 기준

✅ **성공 조건:**
1. https://sedaily.com/ads.txt 접속 가능
2. 내용: `google.com, pub-1326078912759552, DIRECT, f08c47fec0942fa0`
3. Google AdSense에서 "ads.txt 발견됨" 표시

✅ **최종 확인:**
- [ ] 브라우저 확인
- [ ] curl 확인
- [ ] Google 검증 도구 확인
- [ ] AdSense 계정 확인
- [ ] 24-48시간 후 재확인

---

**작성일:** 2026-01-02
**작성자:** [귀하의 이름]
