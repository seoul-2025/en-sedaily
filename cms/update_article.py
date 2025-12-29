#!/usr/bin/env python3
"""
CMS Article Update Script
Updates a single article in DynamoDB with edited content
"""
import boto3
import sys
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


def update_article(news_id: str, updates: dict):
    """Update article in DynamoDB"""
    
    # Build update expression
    update_expr = "SET updated_at = :updated_at"
    expr_values = {':updated_at': datetime.utcnow().isoformat()}
    
    # Add fields to update
    updatable = ['title_en', 'content_en', 'category', 'meta_description', 'keywords', 'hashtags']
    for field in updatable:
        if field in updates:
            update_expr += f", {field} = :{field}"
            expr_values[f':{field}'] = updates[field]
    
    # Update DynamoDB
    response = table.update_item(
        Key={'news_id': news_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    
    return response['Attributes']


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_article.py <news_id>")
        sys.exit(1)
    
    news_id = sys.argv[1]
    
    # Example: Update title
    updates = {
        'title_en': 'Updated Title',
        'content_en': 'Updated content...',
        'category': '경제'
    }
    
    result = update_article(news_id, updates)
    print(f"✅ Updated {news_id}")
    print(f"Title: {result.get('title_en')}")
