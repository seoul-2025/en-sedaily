#!/bin/bash

# Update article detail page to use byline_en
sed -i '' 's/convertByline(article\.byline || '\'''\'')/article.byline_en || '\''Seoul Economic Daily'\''/g' \
  "./frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx"

sed -i '' 's/getReporterNameInEnglish(article\.byline || '\'''\'')/article.byline_en || '\''Seoul Economic Daily'\''/g' \
  "./frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx"

sed -i '' 's/getReporterNameInEnglish(article\.byline)/article.byline_en || '\''Seoul Economic Daily'\''/g' \
  "./frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx"

# Remove unused import
sed -i '' 's/import { convertByline, getReporterNameInEnglish } from "@\/utils\/convertByline";/\/\/ No longer needed: byline_en is pre-translated in backend/g' \
  "./frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx"

echo "✅ Updated article detail page"
