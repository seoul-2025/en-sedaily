## AI Development Guidelines

### Context for AI Assistants

This project uses **Anthropic Claude Opus 4.5** for professional-grade news translation. Before starting any task, AI should:

1. **Check current phase**: Review the timeline section above
2. **Verify environment**: Ensure AWS credentials and API keys are configured
3. **Follow patterns**: Use existing code patterns (especially Lambda handlers)
4. **Update timeline**: Add concise summary after completing tasks
5. **Test translation**: Verify Claude API responses match expected format

### Essential Commands for AI

```bash
# Check project structure
ls -R backend/ frontend/ infrastructure/

# Verify AWS resources
aws lambda list-functions --region us-east-1 | grep seodaily-eng
aws dynamodb list-tables --region us-east-1 | grep seodaily-eng

# Check Lambda logs
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1

# Test translation locally
cd backend && python -m pytest tests/test_translator.py

# Build Lambda package
cd backend && ./build_lambda.sh

# Deploy frontend (SSR)
cd frontend && npm run build && pm2 restart en-sedaily

# Check DynamoDB item count
aws dynamodb scan --table-name seodaily-eng-articles-dev --select COUNT --region us-east-1

# Run migration scripts
python scripts/migrate_timestamps.py --dry-run  # Preview timestamp migration
python scripts/migrate_categories_to_korean.py --dry-run  # Preview category migration
python scripts/migrate_slugs.py --dry-run  # Preview slug generation
```

### Required Checks Before Committing

1. All Lambda functions tested locally
2. Translation output follows TRANSLATION_PROMPT.md format
3. DynamoDB schema matches expected structure
4. Environment variables documented
5. Timeline updated with phase details
6. Cost impact estimated (if applicable)

### Translation Quality Standards

- **Model**: claude-opus-4-5-20251101 only
- **Prompt**: Follow TRANSLATION_PROMPT.md structure
- **Output**: HEADLINE, BYLINE, ARTICLE, DISCLAIMER, SEO/AEO sections
- **Style**: Financial journalism (WSJ/FT/Reuters/Bloomberg)
- **Accuracy**: Preserve facts, numbers, quotes
- **Readability**: Natural English, no machine translation artifacts

---

