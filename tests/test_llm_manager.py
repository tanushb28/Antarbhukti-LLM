#!/usr/bin/env python3
"""
Unit tests for the LLM_Mgr module.
Tests cover LLM initialization, configuration, and API integration with mocking.
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.antarbhukti.llm_manager import LLM_Mgr


class TestLLM_Mgr:
    """Test suite for LLM_Mgr class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Clear environment variables to start fresh
        env_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    def teardown_method(self):
        """Clean up after each test method."""
        # Clear environment variables
        env_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_DEPLOYMENT",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_init_success(self, mock_azure_openai):
        """Test successful LLM_Mgr initialization."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify AzureChatOpenAI was called with correct parameters
        mock_azure_openai.assert_called_once()
        call_args = mock_azure_openai.call_args
        assert call_args[1]["openai_api_key"] == "test_key"
        assert call_args[1]["azure_endpoint"] == "https://test.openai.azure.com/"
        assert call_args[1]["deployment_name"] == "test_deployment"
        # Default version
        assert call_args[1]["openai_api_version"] == "2023-05-15"

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_API_VERSION": "2024-01-01",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_init_with_custom_api_version(self, mock_azure_openai):
        """Test LLM_Mgr initialization with custom API version."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify custom API version is used
        call_args = mock_azure_openai.call_args
        assert call_args[1]["openai_api_version"] == "2024-01-01"

    @patch("src.antarbhukti.llm_manager.load_dotenv")
    def test_init_missing_api_key(self, mock_load_dotenv):
        """Test LLM_Mgr initialization with missing API key."""
        # Don't set AZURE_OPENAI_API_KEY
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = "test_deployment"

        with pytest.raises(
            ValueError, match="Missing required Azure OpenAI credentials"
        ):
            LLM_Mgr()

    @patch("src.antarbhukti.llm_manager.load_dotenv")
    def test_init_missing_endpoint(self, mock_load_dotenv):
        """Test LLM_Mgr initialization with missing endpoint."""
        os.environ["AZURE_OPENAI_API_KEY"] = "test_key"
        # Don't set AZURE_OPENAI_ENDPOINT
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = "test_deployment"

        with pytest.raises(
            ValueError, match="Missing required Azure OpenAI credentials"
        ):
            LLM_Mgr()

    @patch("src.antarbhukti.llm_manager.load_dotenv")
    def test_init_missing_deployment(self, mock_load_dotenv):
        """Test LLM_Mgr initialization with missing deployment."""
        os.environ["AZURE_OPENAI_API_KEY"] = "test_key"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        # Don't set AZURE_OPENAI_DEPLOYMENT

        with pytest.raises(
            ValueError, match="Missing required Azure OpenAI credentials"
        ):
            LLM_Mgr()

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_chat_success(self, mock_azure_openai):
        """Test successful chat interaction."""
        # Mock the LLM response
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        # Mock the invoke method to return a response
        mock_response = Mock()
        mock_response.content = "Test response from LLM"
        mock_llm.invoke.return_value = mock_response

        llm_mgr = LLM_Mgr()

        # Test improve_sfc method
        response = llm_mgr.improve_sfc("Test prompt")

        # Verify response
        assert response == "Test response from LLM"

        # Verify invoke was called with correct message
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].content == "Test prompt"

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_chat_with_exception(self, mock_azure_openai):
        """Test chat interaction with exception."""
        # Mock the LLM to raise an exception
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm
        mock_llm.invoke.side_effect = Exception("API Error")

        llm_mgr = LLM_Mgr()

        # Test that exception is properly handled
        with pytest.raises(Exception, match="API Error"):
            llm_mgr.improve_sfc("Test prompt")

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_extract_code_block_with_python_block(self, mock_azure_openai):
        """Test code block extraction with Python code block."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        llm_mgr = LLM_Mgr()

        # Test with Python code block
        llm_output = """
        Here's the solution:
        
        ```python
        def hello():
            print("Hello, World!")
        ```
        
        This function prints hello.
        """

        extracted = llm_mgr.extract_code_block(llm_output)
        assert "def hello():" in extracted
        assert 'print("Hello, World!")' in extracted

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_extract_code_block_without_language(self, mock_azure_openai):
        """Test code block extraction without language specification."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        llm_mgr = LLM_Mgr()

        # Test with code block without language
        llm_output = """
        Here's the solution:
        
        ```
        def hello():
            print("Hello, World!")
        ```
        
        This function prints hello.
        """

        extracted = llm_mgr.extract_code_block(llm_output)
        assert "def hello():" in extracted
        assert 'print("Hello, World!")' in extracted

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_extract_code_block_no_code_block(self, mock_azure_openai):
        """Test code block extraction when no code block exists."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        llm_mgr = LLM_Mgr()

        # Test with no code block
        llm_output = """
        Here's the solution:
        
        This is just text without any code blocks.
        """

        extracted = llm_mgr.extract_code_block(llm_output)
        assert extracted is None

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_extract_code_block_multiple_blocks(self, mock_azure_openai):
        """Test code block extraction with multiple code blocks."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        llm_mgr = LLM_Mgr()

        # Test with multiple code blocks
        llm_output = """
        Here are two solutions:
        
        ```python
        def hello():
            print("Hello, World!")
        ```
        
        And another one:
        
        ```python
        def goodbye():
            print("Goodbye!")
        ```
        """

        extracted = llm_mgr.extract_code_block(llm_output)
        # Should extract the first code block
        assert "def hello():" in extracted
        assert 'print("Hello, World!")' in extracted

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_streaming_callback_configuration(self, mock_azure_openai):
        """Test that streaming callback is properly configured."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify AzureChatOpenAI was called with streaming callback
        call_args = mock_azure_openai.call_args
        assert "callbacks" in call_args[1]
        callbacks = call_args[1]["callbacks"]
        assert len(callbacks) == 1
        # Check that it's a StreamingStdOutCallbackHandler
        from langchain.callbacks.streaming_stdout import \
            StreamingStdOutCallbackHandler

        assert isinstance(callbacks[0], StreamingStdOutCallbackHandler)

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_temperature_configuration(self, mock_azure_openai):
        """Test that temperature is properly configured."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify temperature is set
        call_args = mock_azure_openai.call_args
        assert "temperature" in call_args[1]
        assert call_args[1]["temperature"] == 0.7

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_max_tokens_configuration(self, mock_azure_openai):
        """Test that max_tokens is properly configured."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify max_tokens is set
        call_args = mock_azure_openai.call_args
        assert "max_tokens" in call_args[1]
        assert call_args[1]["max_tokens"] == 4000

    @patch("src.antarbhukti.llm_manager.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_dotenv_loading(self, mock_azure_openai, mock_load_dotenv):
        """Test that dotenv loading is called."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        LLM_Mgr()

        # Verify load_dotenv was called
        mock_load_dotenv.assert_called_once()

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_static_method_extract_code_block(self, mock_azure_openai):
        """Test static method extract_code_block."""
        # Test static method without creating instance
        llm_output = """
        ```python
        print("Hello from static method")
        ```
        """

        extracted = LLM_Mgr.extract_code_block(llm_output)
        assert 'print("Hello from static method")' in extracted

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_chat_with_empty_prompt(self, mock_azure_openai):
        """Test chat with empty prompt."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        mock_response = Mock()
        mock_response.content = "Please provide a prompt"
        mock_llm.invoke.return_value = mock_response

        llm_mgr = LLM_Mgr()

        # Test with empty prompt
        response = llm_mgr.improve_sfc("")
        assert response == "Please provide a prompt"

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment",
        },
    )
    @patch("src.antarbhukti.llm_manager.AzureChatOpenAI")
    def test_chat_with_very_long_prompt(self, mock_azure_openai):
        """Test chat with very long prompt."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm

        mock_response = Mock()
        mock_response.content = "Response to long prompt"
        mock_llm.invoke.return_value = mock_response

        llm_mgr = LLM_Mgr()

        # Test with very long prompt
        long_prompt = "This is a very long prompt. " * 1000
        response = llm_mgr.improve_sfc(long_prompt)
        assert response == "Response to long prompt"


if __name__ == "__main__":
    pytest.main([__file__])
