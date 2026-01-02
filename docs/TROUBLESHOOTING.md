## Troubleshooting

### Common Issues

**Lambda timeout errors**
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name seodaily-eng-article-collector-dev \
  --timeout 300 \
  --region us-east-1
```

**Translation errors (429 rate limit)**
```python
# Add delay in article_collector.py
await asyncio.sleep(1.0)  # 1 second between translations
```

**DynamoDB throttling**
```bash
# Switch to On-Demand billing mode
aws dynamodb update-table \
  --table-name seodaily-eng-articles-dev \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**Frontend build failures**
```bash
# Clean cache and rebuild
cd frontend
rm -rf .next out node_modules
npm install
npm run build
```

**EC2 memory issues**
```bash
# Check memory usage
free -m

# Restart PM2
pm2 restart en-sedaily

# Clear Next.js cache
rm -rf /var/www/en-sedaily/frontend/.next
```

**SSL certificate renewal**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew --nginx
sudo systemctl reload nginx
```

**Nginx errors**
```bash
# Check Nginx configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

**BigKinds API errors**
```python
# Check API key
response = requests.get(
    "https://tools.kinds.or.kr/search/news",
    headers={"Authorization": f"Bearer {BIGKINDS_API_KEY}"}
)
print(response.status_code)
```

**Manual article collection**
```bash
# Trigger Lambda manually
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json

cat response.json
```

---

