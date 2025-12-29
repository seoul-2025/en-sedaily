# Development Guidelines

## Code Quality Standards

### Documentation
- **Module Docstrings**: Every Python module starts with triple-quoted docstring describing purpose
- **Function Docstrings**: All functions include docstrings with Args, Returns, Raises sections
- **Inline Comments**: Used sparingly for complex logic, not obvious code
- **Type Hints**: Comprehensive type annotations for all function parameters and returns

### Naming Conventions
- **Python**: snake_case for functions/variables, PascalCase for classes
- **TypeScript**: camelCase for functions/variables, PascalCase for components/types
- **Constants**: UPPER_SNAKE_CASE for configuration values
- **Private Methods**: Prefix with underscore (_method_name)
- **Descriptive Names**: Clear, self-documenting names (e.g., `validate_bigkinds_search_response` not `validate_resp`)

### File Organization
- **Imports**: Grouped in order: standard library, third-party, local imports
- **Class Structure**: Static methods, class methods, then instance methods
- **Logical Grouping**: Related functions grouped together with clear separation
- **Single Responsibility**: Each module/class has one clear purpose

## Structural Conventions

### Backend Architecture

#### Handler Pattern
```python
class SearchHandler:
    """Handler for search operations"""
    
    def __init__(self, bigkinds_client, translation_service, cache_manager):
        self.bigkinds_client = bigkinds_client
        self.translation_service = translation_service
        self.cache_manager = cache_manager
    
    async def handle_search(self, query: str, filters: SearchFilters, 
                           page: int, page_size: int) -> SearchResponse:
        """Main handler method with clear parameters"""
        # Implementation
```

**Pattern**: Handlers receive dependencies via constructor injection, expose single public method for operation

#### Error Handling Pattern
```python
try:
    # Operation
    result = await handler.handle_search(...)
except SearchHandlerError as e:
    logger.error(f"Search handler error: {e}")
    raise HTTPException(status_code=400, detail={...})
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail={...})
finally:
    # Cleanup resources
    if client:
        await client.close()
```

**Pattern**: Specific exceptions caught first, generic Exception last, always cleanup in finally block

#### Validation Pattern
```python
@staticmethod
def validate_bigkinds_search_response(response_data: Dict[str, Any]) -> None:
    """Validate response structure"""
    if not isinstance(response_data, dict):
        raise ResponseValidationError("Response must be a dictionary")
    
    if "return_object" not in response_data:
        raise ResponseValidationError("Response missing 'return_object' field")
    
    # Continue validation...
```

**Pattern**: Static methods for stateless validation, raise custom exceptions with descriptive messages

#### Sanitization Pattern
```python
@staticmethod
def validate_and_sanitize_bigkinds_search(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize response"""
    ResponseValidator.validate_bigkinds_search_response(response_data)
    
    sanitized = {
        "return_object": {
            "total_hits": return_object["total_hits"],
            "documents": []
        }
    }
    
    for doc in return_object["documents"]:
        sanitized_doc = {
            "news_id": doc.get("news_id", ""),
            "title": doc.get("title", ""),
            # Provide defaults for all fields
        }
        sanitized["return_object"]["documents"].append(sanitized_doc)
    
    return sanitized
```

**Pattern**: Validate first, then create new sanitized dict with defaults for missing fields

### Frontend Architecture

#### Client Component Pattern
```typescript
'use client';

export default function SearchPage() {
  const [articles, setArticles] = useState<CategoryArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  useEffect(() => {
    setLoading(true);
    searchArticles(query, page, pageSize)
      .then(data => {
        setArticles(data.articles || []);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to search articles. Please try again.');
        setLoading(false);
      });
  }, [query, page]);
  
  return (
    <>
      {loading && <LoadingSkeleton />}
      {error && <ErrorMessage />}
      {articles.length > 0 && <ArticleList />}
    </>
  );
}
```

**Pattern**: Client components use 'use client' directive, manage state with useState, side effects with useEffect, conditional rendering for loading/error/success states

#### Suspense Wrapper Pattern
```typescript
export default function SearchPage() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <SearchResults />
    </Suspense>
  );
}
```

**Pattern**: Wrap components using useSearchParams with Suspense boundary for proper SSR handling

#### API Utility Pattern
```typescript
export async function searchArticles(
  query: string, 
  page: number = 1, 
  pageSize: number = 20
): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filters, page, page_size: pageSize })
  });
  
  if (!response.ok) {
    throw new Error('Search failed');
  }
  
  return response.json();
}
```

**Pattern**: Centralized API functions in utils/api.ts, typed parameters and returns, proper error handling

## Testing Practices

### Property-Based Testing
```python
@pytest.mark.asyncio
@given(
    selected_providers=st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3, unique=True),
    num_articles=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
async def test_provider_filtering_accuracy(selected_providers, num_articles):
    """
    For any set of selected news providers, all returned articles should be from those providers only.
    Validates: Requirements 2.2
    """
    # Test implementation
```

**Pattern**: Use Hypothesis for property-based testing, test invariants across many generated inputs, link to requirements

### Mock Pattern
```python
# Create mock services
bigkinds_client = Mock()
translation_service = Mock()
cache_manager = Mock()

# Mock async methods
bigkinds_client.search_news = AsyncMock(return_value=search_result)
translation_service.translate = AsyncMock(side_effect=lambda text, **kwargs: f"Translated: {text}")

# Mock sync methods
cache_manager.generate_cache_key = Mock(side_effect=lambda aid, field, lang: f"{aid}:{field}:{lang}")
```

**Pattern**: Use Mock for sync methods, AsyncMock for async methods, side_effect for dynamic return values

### Test Structure
```python
async def test_feature():
    """Test description with requirements reference"""
    # Arrange: Setup test data and mocks
    articles = [...]
    bigkinds_client.search_news = AsyncMock(return_value=search_result)
    
    # Act: Execute the operation
    response = await handler.handle_search(...)
    
    # Assert: Verify results
    assert response.total_hits == expected_total
    assert len(response.articles) == expected_count
    bigkinds_client.search_news.assert_called_once()
```

**Pattern**: Arrange-Act-Assert structure, clear separation of setup/execution/verification

## Security Practices

### Sensitive Data Sanitization
```python
@staticmethod
def _sanitize_log_message(message: str, sensitive_keys: list = None) -> str:
    """Remove sensitive information from log messages"""
    if sensitive_keys is None:
        sensitive_keys = [
            "api_key", "access_key", "secret", "password",
            "token", "authorization"
        ]
    
    import re
    sanitized = message
    
    for key in sensitive_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\s*[=:]\s*\S+', re.IGNORECASE)
        sanitized = pattern.sub(f"{key}=[REDACTED]", sanitized)
    
    return sanitized
```

**Pattern**: Always sanitize logs before writing, use regex to redact sensitive patterns, provide default sensitive key list

### Environment Variables
```python
class Settings(BaseSettings):
    bigkinds_api_key: str
    anthropic_api_key: str
    
    class Config:
        env_file = ".env"
```

**Pattern**: Use Pydantic Settings for configuration, never hardcode secrets, load from .env files

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Pattern**: Explicit CORS configuration, comment about production requirements

## Error Handling Standards

### User-Friendly Error Messages
```python
return ErrorResponse(
    code=ErrorCode.BIGKINDS_NOT_FOUND.value,
    message="The requested article was not found. It may have been removed or the ID is invalid.",
    retry_possible=False
)
```

**Pattern**: Never expose technical details to users, provide actionable guidance, indicate if retry is possible

### Error Response Structure
```python
@dataclass
class ErrorResponse:
    """Standardized error response"""
    code: str
    message: str
    retry_possible: bool
    details: Optional[Dict[str, Any]] = None
```

**Pattern**: Consistent error structure across all handlers, use dataclasses for type safety

### Centralized Error Handling
```python
class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception) -> ErrorResponse:
        """Main error handler that routes to specific handlers"""
        if isinstance(error, ValidationError):
            return ErrorHandler.handle_validation_error(error)
        elif isinstance(error, TranslationError):
            return ErrorHandler.handle_translation_error(error)
        # ... more specific handlers
        else:
            return ErrorHandler.handle_unexpected_error(error)
```

**Pattern**: Single entry point for error handling, route to specific handlers based on exception type

## Async/Await Patterns

### Async Function Definition
```python
async def handle_search(self, query: str, filters: SearchFilters, 
                       page: int, page_size: int) -> SearchResponse:
    """Async handler for search operations"""
    result = await self.bigkinds_client.search_news(...)
    translated = await self.translation_service.translate(...)
    return SearchResponse(...)
```

**Pattern**: All I/O operations are async, use await for async calls, return typed responses

### Resource Cleanup
```python
finally:
    if bigkinds_client:
        await bigkinds_client.close()
    if cache_manager:
        await cache_manager.close()
```

**Pattern**: Always cleanup async resources in finally block, check for None before closing

## UI/UX Patterns

### Loading States
```typescript
{loading && (
  <div className="space-y-6">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
      </div>
    ))}
  </div>
)}
```

**Pattern**: Skeleton screens for loading states, multiple skeleton items to show expected layout

### Error States
```typescript
{error && (
  <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded">
    <div className="flex items-start gap-3">
      <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
      <div>
        <h3 className="font-semibold text-red-800 mb-1">Error</h3>
        <p className="text-red-700">{error}</p>
        <button onClick={() => window.location.reload()}>Try Again</button>
      </div>
    </div>
  </div>
)}
```

**Pattern**: Clear error messages with icon, actionable button to retry, semantic colors

### Empty States
```typescript
{!loading && articles.length === 0 && (
  <div className="text-center py-16 bg-gray-50 rounded-lg">
    <SearchIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
    <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
    <p className="text-gray-600">Try different keywords or check your spelling</p>
  </div>
)}
```

**Pattern**: Helpful empty states with icon, clear message, guidance for next action

### Pagination
```typescript
const renderPagination = () => {
  if (totalPages <= 1) return null;
  
  const maxVisible = 7;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);
  
  // Show first page, ellipsis, visible range, ellipsis, last page
  return (
    <div className="flex items-center justify-center gap-2 py-8">
      <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
        Previous
      </button>
      {/* Page buttons */}
      <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>
        Next
      </button>
    </div>
  );
};
```

**Pattern**: Smart pagination with ellipsis, Previous/Next buttons, disabled states, centered layout

## Performance Optimizations

### Batch Operations
```python
# Instead of individual get_item calls
existing_ids = await dynamodb_client.batch_check_exists([a.news_id for a in articles])
```

**Pattern**: Use batch operations for DynamoDB (100 items per batch), reduces API calls by 91%

### Chunked Processing
```python
chunks = [content[i:i+4000] for i in range(0, len(content), 4000)]
translated = ''.join([await translate(chunk) for chunk in chunks])
```

**Pattern**: Split large content into chunks to avoid API limits, process sequentially, join results

### Client-Side Caching
```typescript
useEffect(() => {
  fetchLatestArticles().then(setArticles);
}, []); // Empty dependency array = fetch once on mount
```

**Pattern**: Fetch data once on component mount, store in state, avoid unnecessary re-fetches

## Code Idioms

### Optional Chaining
```typescript
const title = article?.title || 'Untitled';
const images = article?.images || [];
```

**Pattern**: Use optional chaining for potentially undefined values, provide sensible defaults

### Array Mapping with Keys
```typescript
{articles.map((article) => (
  <article key={article.news_id}>
    {/* Content */}
  </article>
))}
```

**Pattern**: Always provide unique key prop for mapped elements, use stable identifiers (news_id)

### Conditional Rendering
```typescript
{loading && <LoadingSkeleton />}
{error && <ErrorMessage />}
{!loading && !error && articles.length > 0 && <ArticleList />}
```

**Pattern**: Use && for conditional rendering, check multiple conditions for complex states

### Default Parameters
```python
async def search_news(
    self,
    query: str,
    published_from: str,
    published_until: str,
    providers: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    return_from: int = 0,
    return_size: int = 10
) -> SearchResult:
```

**Pattern**: Provide sensible defaults for optional parameters, use Optional[] for nullable types

## Logging Standards

### Log Levels
```python
logger.info(f"Processing {len(articles)} articles")
logger.warning(f"Validation error: {sanitized_error}")
logger.error(f"BigKinds API error: {sanitized_error}")
logger.error(f"Unexpected error: {sanitized_error}", exc_info=True)
```

**Pattern**: INFO for normal operations, WARNING for validation issues, ERROR for failures, exc_info=True for stack traces

### Structured Logging
```python
logger.error(
    f"Unexpected error: {sanitized_error}",
    exc_info=True,
    extra={"error_type": type(error).__name__}
)
```

**Pattern**: Include context in extra dict, sanitize before logging, use exc_info for debugging

## API Design

### Request Validation
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="English search query")
    filters: SearchFiltersRequest
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=10, ge=1, le=100, description="Results per page")
```

**Pattern**: Use Pydantic models for request validation, Field() for constraints and descriptions

### Response Models
```python
class SearchResponse(BaseModel):
    total_hits: int
    page: int
    page_size: int
    total_pages: int
    articles: List[ArticleSummary]
```

**Pattern**: Explicit response models, typed fields, consistent structure across endpoints

### Endpoint Documentation
```python
@app.post(
    "/api/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Search Korean news articles",
    description="Search for Korean news articles using English keywords with filtering and pagination"
)
```

**Pattern**: Document all responses, provide summary and description, specify error models

## Common Annotations

### Python Type Hints
```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ErrorResponse:
    code: str
    message: str
    retry_possible: bool
    details: Optional[Dict[str, Any]] = None
```

**Pattern**: Use typing module for complex types, dataclasses for data structures, Optional for nullable

### TypeScript Types
```typescript
interface CategoryArticle {
  news_id: string;
  title: string;
  published_at: string;
  category: string;
  provider?: string;
}

type SearchResponse = {
  total_hits: number;
  page: number;
  articles: CategoryArticle[];
};
```

**Pattern**: Use interface for object shapes, type for unions/aliases, ? for optional properties

### Pytest Markers
```python
@pytest.mark.asyncio
@given(...)
@settings(max_examples=100)
async def test_feature():
    """Test description"""
```

**Pattern**: Mark async tests with @pytest.mark.asyncio, use @given for property-based tests, @settings for configuration
