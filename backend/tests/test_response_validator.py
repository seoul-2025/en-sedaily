"""
Property-based tests for API response validation
Tests response integrity validation before processing
"""
import pytest
from hypothesis import given, strategies as st, assume
from clients.response_validator import ResponseValidator, ResponseValidationError


# Strategies for generating test data
@st.composite
def valid_bigkinds_search_response(draw):
    """Generate valid BigKinds search response structure"""
    num_docs = draw(st.integers(min_value=0, max_value=20))
    documents = []
    
    for _ in range(num_docs):
        doc = {
            "news_id": draw(st.text(min_size=1, max_size=50)),
            "title": draw(st.text(min_size=0, max_size=200)),
            "content": draw(st.one_of(st.none(), st.text(max_size=1000))),
            "published_at": draw(st.text(min_size=0, max_size=50)),
            "provider_name": draw(st.text(min_size=0, max_size=100)),
            "category": draw(st.text(min_size=0, max_size=50)),
            "byline": draw(st.one_of(st.none(), st.text(max_size=100))),
            "news_url": draw(st.one_of(st.none(), st.text(max_size=200))),
            "images": draw(st.lists(st.text(max_size=200), max_size=5)),
            "images_caption": draw(st.lists(st.text(max_size=200), max_size=5))
        }
        documents.append(doc)
    
    return {
        "return_object": {
            "total_hits": draw(st.integers(min_value=0, max_value=10000)),
            "documents": documents
        }
    }


@st.composite
def valid_bigkinds_detail_response(draw):
    """Generate valid BigKinds detail response structure"""
    num_docs = draw(st.integers(min_value=0, max_value=10))
    documents = []
    
    for _ in range(num_docs):
        doc = {
            "news_id": draw(st.text(min_size=1, max_size=50)),
            "title": draw(st.text(min_size=0, max_size=200)),
            "content": draw(st.one_of(st.none(), st.text(max_size=1000))),
            "published_at": draw(st.text(min_size=0, max_size=50)),
            "provider_name": draw(st.text(min_size=0, max_size=100)),
            "category": draw(st.text(min_size=0, max_size=50)),
            "byline": draw(st.one_of(st.none(), st.text(max_size=100))),
            "news_url": draw(st.one_of(st.none(), st.text(max_size=200))),
            "images": draw(st.lists(st.text(max_size=200), max_size=5)),
            "images_caption": draw(st.lists(st.text(max_size=200), max_size=5))
        }
        documents.append(doc)
    
    return {
        "return_object": {
            "documents": documents
        }
    }


@st.composite
def valid_translation_response(draw):
    """Generate valid translation response structure"""
    # Generate text that is not just whitespace
    text = draw(st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    return {
        "content": [
            {
                "text": text
            }
        ]
    }


@st.composite
def malformed_bigkinds_search_response(draw):
    """Generate malformed BigKinds search responses"""
    malformed_types = [
        # Missing return_object
        st.just({"some_other_field": "value"}),
        # return_object is not a dict
        st.just({"return_object": "not a dict"}),
        # Missing total_hits
        st.just({"return_object": {"documents": []}}),
        # total_hits is not an integer
        st.just({"return_object": {"total_hits": "not an int", "documents": []}}),
        # total_hits is negative
        st.just({"return_object": {"total_hits": -1, "documents": []}}),
        # Missing documents
        st.just({"return_object": {"total_hits": 0}}),
        # documents is not a list
        st.just({"return_object": {"total_hits": 0, "documents": "not a list"}}),
        # Document missing news_id
        st.just({"return_object": {"total_hits": 1, "documents": [{"title": "test"}]}}),
        # Document news_id is not a string
        st.just({"return_object": {"total_hits": 1, "documents": [{"news_id": 123}]}}),
        # Response is not a dict
        st.just("not a dict"),
        st.just([]),
        st.just(None),
    ]
    return draw(st.one_of(*malformed_types))


@st.composite
def malformed_translation_response(draw):
    """Generate malformed translation responses"""
    malformed_types = [
        # Missing content
        st.just({"some_other_field": "value"}),
        # content is not a list
        st.just({"content": "not a list"}),
        # content is empty list
        st.just({"content": []}),
        # content item is not a dict
        st.just({"content": ["not a dict"]}),
        # content item missing text
        st.just({"content": [{"some_field": "value"}]}),
        # text is not a string
        st.just({"content": [{"text": 123}]}),
        # text is empty string
        st.just({"content": [{"text": ""}]}),
        # text is whitespace only
        st.just({"content": [{"text": "   "}]}),
        # Response is not a dict
        st.just("not a dict"),
        st.just([]),
        st.just(None),
    ]
    return draw(st.one_of(*malformed_types))


class TestResponseValidatorProperties:
    """Property-based tests for response validation"""
    
    @given(valid_bigkinds_search_response())
    def test_property_46_valid_bigkinds_search_accepted(self, response_data):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any valid BigKinds search response, validation should pass
        Validates: Requirements 10.5
        """
        # Valid responses should not raise an exception
        try:
            validated = ResponseValidator.validate_and_sanitize_bigkinds_search(response_data)
            
            # Verify structure is preserved
            assert "return_object" in validated
            assert "total_hits" in validated["return_object"]
            assert "documents" in validated["return_object"]
            assert isinstance(validated["return_object"]["documents"], list)
            
            # Verify all documents have required fields
            for doc in validated["return_object"]["documents"]:
                assert "news_id" in doc
                assert isinstance(doc["news_id"], str)
        except ResponseValidationError:
            pytest.fail("Valid response should not raise ResponseValidationError")
    
    @given(malformed_bigkinds_search_response())
    def test_property_46_malformed_bigkinds_search_rejected(self, response_data):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any malformed BigKinds search response, validation should fail
        Validates: Requirements 10.5
        """
        # Malformed responses should raise ResponseValidationError
        with pytest.raises(ResponseValidationError):
            ResponseValidator.validate_and_sanitize_bigkinds_search(response_data)
    
    @given(valid_bigkinds_detail_response())
    def test_property_46_valid_bigkinds_detail_accepted(self, response_data):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any valid BigKinds detail response, validation should pass
        Validates: Requirements 10.5
        """
        # Valid responses should not raise an exception
        try:
            validated = ResponseValidator.validate_and_sanitize_bigkinds_detail(response_data)
            
            # Verify structure is preserved
            assert "return_object" in validated
            assert "documents" in validated["return_object"]
            assert isinstance(validated["return_object"]["documents"], list)
            
            # Verify all documents have required fields
            for doc in validated["return_object"]["documents"]:
                assert "news_id" in doc
                assert isinstance(doc["news_id"], str)
        except ResponseValidationError:
            pytest.fail("Valid response should not raise ResponseValidationError")
    
    @given(valid_translation_response())
    def test_property_46_valid_translation_accepted(self, response_data):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any valid translation response, validation should pass
        Validates: Requirements 10.5
        """
        # Valid responses should not raise an exception
        try:
            validated = ResponseValidator.validate_and_sanitize_translation(response_data)
            
            # Verify structure is preserved
            assert "content" in validated
            assert isinstance(validated["content"], list)
            assert len(validated["content"]) > 0
            assert "text" in validated["content"][0]
            assert isinstance(validated["content"][0]["text"], str)
            assert validated["content"][0]["text"].strip()  # Not empty
        except ResponseValidationError:
            pytest.fail("Valid response should not raise ResponseValidationError")
    
    @given(malformed_translation_response())
    def test_property_46_malformed_translation_rejected(self, response_data):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any malformed translation response, validation should fail
        Validates: Requirements 10.5
        """
        # Malformed responses should raise ResponseValidationError
        with pytest.raises(ResponseValidationError):
            ResponseValidator.validate_and_sanitize_translation(response_data)
    
    @given(
        st.integers(min_value=0, max_value=10),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)
    )
    def test_property_46_sanitization_adds_defaults(self, total_hits, news_ids):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        For any valid response, sanitization should add default values for missing optional fields
        Validates: Requirements 10.5
        """
        # Create minimal valid response
        response_data = {
            "return_object": {
                "total_hits": total_hits,
                "documents": [
                    {"news_id": news_id}
                    for news_id in news_ids
                ]
            }
        }
        
        validated = ResponseValidator.validate_and_sanitize_bigkinds_search(response_data)
        
        # Verify defaults are added
        for doc in validated["return_object"]["documents"]:
            assert "title" in doc
            assert "content" in doc
            assert "published_at" in doc
            assert "provider_name" in doc
            assert "category" in doc
            assert "byline" in doc
            assert "news_url" in doc
            assert "images" in doc
            assert "images_caption" in doc
            
            # Verify defaults are appropriate types
            assert isinstance(doc["title"], str)
            assert isinstance(doc["published_at"], str)
            assert isinstance(doc["provider_name"], str)
            assert isinstance(doc["category"], str)
            assert isinstance(doc["images"], list)
            assert isinstance(doc["images_caption"], list)
    
    def test_property_46_response_not_dict_rejected(self):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        Non-dictionary responses should be rejected
        Validates: Requirements 10.5
        """
        # Test various non-dict types
        invalid_responses = [
            "string response",
            123,
            [],
            None,
            True
        ]
        
        for invalid_response in invalid_responses:
            with pytest.raises(ResponseValidationError, match="must be a dictionary"):
                ResponseValidator.validate_bigkinds_search_response(invalid_response)
    
    @given(st.integers(max_value=-1))
    def test_property_46_negative_total_hits_rejected(self, negative_hits):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        Negative total_hits values should be rejected
        Validates: Requirements 10.5
        """
        response_data = {
            "return_object": {
                "total_hits": negative_hits,
                "documents": []
            }
        }
        
        with pytest.raises(ResponseValidationError, match="cannot be negative"):
            ResponseValidator.validate_bigkinds_search_response(response_data)
    
    @given(st.lists(st.dictionaries(st.text(), st.text()), min_size=1, max_size=5))
    def test_property_46_documents_without_news_id_rejected(self, documents):
        """
        Feature: seodaily-eng, Property 46: API responses are validated before processing
        Documents without news_id should be rejected
        Validates: Requirements 10.5
        """
        # Ensure none of the documents have news_id
        for doc in documents:
            if "news_id" in doc:
                del doc["news_id"]
        
        response_data = {
            "return_object": {
                "total_hits": len(documents),
                "documents": documents
            }
        }
        
        with pytest.raises(ResponseValidationError, match="missing 'news_id'"):
            ResponseValidator.validate_bigkinds_search_response(response_data)


# Unit tests for specific edge cases
class TestResponseValidatorEdgeCases:
    """Unit tests for specific edge cases in response validation"""
    
    def test_empty_documents_list_valid(self):
        """Empty documents list should be valid"""
        response_data = {
            "return_object": {
                "total_hits": 0,
                "documents": []
            }
        }
        
        # Should not raise
        validated = ResponseValidator.validate_and_sanitize_bigkinds_search(response_data)
        assert validated["return_object"]["documents"] == []
    
    def test_translation_with_whitespace_text_rejected(self):
        """Translation response with only whitespace should be rejected"""
        response_data = {
            "content": [
                {"text": "   \n\t  "}
            ]
        }
        
        with pytest.raises(ResponseValidationError, match="empty"):
            ResponseValidator.validate_translation_response(response_data)
    
    def test_document_with_non_string_news_id_rejected(self):
        """Document with non-string news_id should be rejected"""
        response_data = {
            "return_object": {
                "total_hits": 1,
                "documents": [
                    {"news_id": 12345}  # Integer instead of string
                ]
            }
        }
        
        with pytest.raises(ResponseValidationError, match="must be a string"):
            ResponseValidator.validate_bigkinds_search_response(response_data)
