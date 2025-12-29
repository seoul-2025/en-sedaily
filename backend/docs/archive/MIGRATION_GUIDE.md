# Slug Migration Guide

7,889개 기존 기사에 SEO 친화적 slug를 추가하는 가이드입니다.

## 📋 사전 준비 사항

### 1. AWS 자격증명 확인
```bash
aws sts get-caller-identity
```

출력 예시:
```json
{
    "UserId": "...",
    "Account": "887078546492",
    "Arn": "arn:aws:iam::887078546492:user/..."
}
```

### 2. DynamoDB 테이블 확인
```bash
aws dynamodb describe-table \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --query 'Table.[TableName,ItemCount,TableStatus]'
```

### 3. Python 의존성 확인
```bash
cd backend
pip3 install boto3
```

---

## 🚀 Step 1: GSI 생성 (30분 소요)

### GSI 생성 스크립트 실행
```bash
cd backend/scripts
./create_gsi.sh
```

**예상 출력**:
```
==================================================
Creating Global Secondary Index for Slug Lookups
==================================================

Table: seodaily-eng-articles-dev
Region: us-east-1
Index: slug-index

1. Checking if table exists...
✓ Table exists

2. Checking if GSI already exists...
✓ GSI does not exist yet

3. Creating GSI 'slug-index'...
   This will take 10-30 minutes to complete...

✓ GSI creation initiated successfully

4. Monitoring GSI creation status...
   Status: CREATING... (waiting)
   Status: CREATING... (waiting)
   ...

✓ GSI creation completed successfully!
```

### 수동 GSI 생성 (스크립트 실패 시)
```bash
aws dynamodb update-table \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --attribute-definitions AttributeName=slug,AttributeType=S \
  --global-secondary-indexes \
    "[{
      \"Create\": {
        \"IndexName\": \"slug-index\",
        \"KeySchema\": [{\"AttributeName\":\"slug\",\"KeyType\":\"HASH\"}],
        \"Projection\": {\"ProjectionType\":\"ALL\"},
        \"ProvisionedThroughput\": {
          \"ReadCapacityUnits\": 5,
          \"WriteCapacityUnits\": 5
        }
      }
    }]"
```

### GSI 상태 확인
```bash
aws dynamodb describe-table \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --query 'Table.GlobalSecondaryIndexes[0].[IndexName,IndexStatus]'
```

**ACTIVE 상태가 되면 다음 단계로 진행**

---

## 🧪 Step 2: Dry Run 테스트 (1분 소요)

### 전체 미리보기
```bash
cd backend
python3 scripts/migrate_slugs.py --dry-run
```

**예상 출력**:
```
2025-12-22 14:30:00 [INFO] Starting Slug Migration (dry_run=True)
2025-12-22 14:30:01 [INFO] Scanning all articles from table...
2025-12-22 14:30:05 [INFO] ✓ Total articles found: 7889

2025-12-22 14:30:05 [INFO] --- Batch 1/158 ---
2025-12-22 14:30:05 [INFO] [DRY RUN] Would migrate 02100311.20251222: 'Samsung Q4...' → 'samsung-q4-earnings-beat-expectations'
...

===============================================================
MIGRATION COMPLETE
===============================================================
Total articles:             7889
Migrated:                   7650
Skipped (already had slug): 239
Failed:                     0
Duration:                   45.23 seconds
===============================================================

This was a DRY RUN - no changes were made to DynamoDB
```

### 샘플 테스트 (처음 10개만)
```bash
python3 scripts/migrate_slugs.py --dry-run --sample 10
```

---

## ✅ Step 3: 실제 마이그레이션 (10분 소요)

### ⚠️ 주의사항
- **백업 확인**: DynamoDB Point-in-Time Recovery 활성화 확인
- **타이밍**: 트래픽이 적은 시간대 (새벽 2-4시) 권장
- **모니터링**: CloudWatch 로그 모니터링 준비

### 마이그레이션 실행
```bash
cd backend
python3 scripts/migrate_slugs.py
```

**예상 출력**:
```
2025-12-22 02:30:00 [INFO] Starting Slug Migration (dry_run=False)
2025-12-22 02:30:05 [INFO] ✓ Total articles found: 7889

2025-12-22 02:30:05 [INFO] --- Batch 1/158 ---
2025-12-22 02:30:05 [INFO] ✓ Migrated 02100311.20251222: samsung-q4-earnings-beat-expectations
2025-12-22 02:30:06 [INFO] ✓ Migrated 02100311.20251221: sk-hynix-unveils-next-gen-ai-chips
2025-12-22 02:30:06 [INFO] Skipping 02100311.20251220: slug already exists (korea-economy-grows)
...

===============================================================
MIGRATION COMPLETE
===============================================================
Total articles:             7889
Migrated:                   7650
Skipped (already had slug): 239
Failed:                     0
Duration:                   582.45 seconds (9.7 minutes)
Rate:                       13.14 articles/sec
===============================================================

✓ Migration completed successfully
```

### 진행 중 중단하려면
`Ctrl+C` 누르면 안전하게 중단됩니다. 이미 처리된 기사는 slug가 저장된 상태이고, 나머지는 다시 실행하면 이어서 진행됩니다.

---

## 🔍 Step 4: 검증

### 1. 랜덤 샘플 확인
```bash
aws dynamodb scan \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --projection-expression "news_id,slug,title_en" \
  --limit 10
```

**예상 출력**:
```json
{
    "Items": [
        {
            "news_id": "02100311.20251222092834001",
            "slug": "samsung-q4-earnings-beat-expectations",
            "title_en": "Samsung Q4 Earnings Beat Expectations"
        },
        ...
    ]
}
```

### 2. slug 필드 통계
```bash
# Slug가 있는 기사 수
aws dynamodb scan \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --filter-expression "attribute_exists(slug)" \
  --select COUNT
```

**예상**:
```json
{
    "Count": 7889,
    "ScannedCount": 7889
}
```

### 3. GSI 쿼리 테스트
```bash
# 특정 slug로 기사 조회
aws dynamodb query \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --index-name slug-index \
  --key-condition-expression "slug = :slug" \
  --expression-attribute-values '{":slug":{"S":"samsung-q4-earnings-beat-expectations"}}'
```

**성공 시**: 해당 기사 데이터가 반환됨

---

## 🔄 롤백 (문제 발생 시)

### Slug 필드 제거
```python
# rollback_slugs.py
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')

# Scan all items
response = table.scan(ProjectionExpression='news_id')

# Remove slug from each item
for item in response['Items']:
    table.update_item(
        Key={'news_id': item['news_id']},
        UpdateExpression='REMOVE slug'
    )
    print(f"Removed slug from {item['news_id']}")
```

### GSI 삭제
```bash
aws dynamodb update-table \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --global-secondary-index-updates \
    '[{"Delete": {"IndexName": "slug-index"}}]'
```

---

## 📊 예상 소요 시간

| 단계 | 작업 | 소요 시간 |
|------|------|-----------|
| 1 | GSI 생성 | 10-30분 |
| 2 | Dry Run 테스트 | 1분 |
| 3 | 실제 마이그레이션 | 10분 |
| 4 | 검증 | 5분 |
| **총계** | | **30-50분** |

---

## ❓ 문제 해결

### Q1: "Failed to scan table" 에러
**원인**: AWS 자격증명 문제
**해결**:
```bash
aws configure
# 또는
export AWS_PROFILE=your-profile-name
```

### Q2: "IndexNotFoundException" 에러
**원인**: GSI가 아직 생성 중이거나 실패
**해결**:
```bash
# GSI 상태 확인
aws dynamodb describe-table \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --query 'Table.GlobalSecondaryIndexes'

# ACTIVE 상태가 될 때까지 대기
```

### Q3: "ProvisionedThroughputExceededException" 에러
**원인**: Write 용량 초과
**해결**:
```bash
# 배치 크기 줄이기
python3 scripts/migrate_slugs.py --batch-size 25
```

### Q4: 일부 기사 실패
**원인**: title_en 누락 등
**해결**: 로그에서 실패한 기사 확인 후 수동 처리
```bash
# 실패한 기사만 재시도
python3 scripts/migrate_slugs.py --retry-failed
```

---

## ✅ 완료 체크리스트

- [ ] AWS 자격증명 확인
- [ ] DynamoDB 테이블 확인
- [ ] GSI 생성 완료 (ACTIVE 상태)
- [ ] Dry run 테스트 성공
- [ ] 실제 마이그레이션 완료
- [ ] 랜덤 샘플 검증
- [ ] GSI 쿼리 테스트 성공
- [ ] CloudWatch 로그 확인

---

## 📞 지원

문제 발생 시:
1. 로그 파일 확인: `tail -f migration.log`
2. CloudWatch 로그 확인
3. GitHub Issue 등록

**작성일**: 2025-12-22
**버전**: 1.0
