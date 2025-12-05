"""
LLM Provider Module
Handles initialization and configuration of different LLM providers.
"""

import os
from typing import Optional, Literal, cast
from langchain_community.chat_models.litellm import ChatLiteLLM


class LLMProviderFactory:
    """Factory class for creating LLM instances from different providers."""
    
    @staticmethod
    def create_llm(
        provider: Optional[Literal["openai", "watsonx", "vllm"]] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        watsonx_api_key: Optional[str] = None,
        watsonx_project_id: Optional[str] = None,
        watsonx_url: Optional[str] = None,
        vllm_api_base: Optional[str] = None,
        vllm_api_key: Optional[str] = None,
        **kwargs
    ) -> ChatLiteLLM:
        """
        Create an LLM instance based on the specified provider.
        All parameters can be loaded from environment variables if not provided.
        
        Environment Variables:
            LLM_PROVIDER: The LLM provider to use (default: "openai")
            MODEL_NAME: The model name (default: "gpt-4o-mini")
            TEMPERATURE: The temperature for response generation (default: 0.7)
            OPENAI_API_KEY: OpenAI API key (required for OpenAI provider)
            WATSONX_API_KEY: Watsonx API key (required for Watsonx provider)
            WATSONX_PROJECT_ID: Watsonx project ID (required for Watsonx provider)
            WATSONX_URL: Watsonx URL (default: "https://us-south.ml.cloud.ibm.com")
            VLLM_API_BASE: vLLM API base URL (required for vLLM provider)
            VLLM_API_KEY: vLLM API key (optional, for authenticated endpoints)
        
        Args:
            provider: The LLM provider to use (loaded from LLM_PROVIDER env var if not provided)
            model_name: The name of the model to use (loaded from MODEL_NAME env var if not provided)
            temperature: The temperature for response generation (loaded from TEMPERATURE env var if not provided)
            watsonx_api_key: Watsonx API key (loaded from WATSONX_API_KEY env var if not provided)
            watsonx_project_id: Watsonx project ID (loaded from WATSONX_PROJECT_ID env var if not provided)
            watsonx_url: Watsonx URL (loaded from WATSONX_URL env var if not provided)
            vllm_api_base: vLLM API base URL (loaded from VLLM_API_BASE env var if not provided)
            vllm_api_key: vLLM API key (loaded from VLLM_API_KEY env var if not provided)
            **kwargs: Additional parameters to pass to the LLM
            
        Returns:
            Configured ChatLiteLLM instance
            
        Raises:
            ValueError: If required credentials are missing for the specified provider
        """
        # Read configuration from environment variables with fallbacks
        if provider is None:
            provider_env = os.getenv("LLM_PROVIDER", "openai")
            provider = cast(Literal["openai", "watsonx", "vllm"],
                          provider_env if provider_env in ["openai", "watsonx", "vllm"] else "openai")
        
        model_name = model_name or os.getenv("MODEL_NAME", "gpt-4o-mini")
        
        # Read temperature from environment variable, convert to float if present
        if temperature is None:
            temp_env = os.getenv("TEMPERATURE")
            temperature = float(temp_env) if temp_env else 0.7
        
        if provider == "watsonx":
            return LLMProviderFactory._create_watsonx_llm(
                model_name=model_name,
                temperature=temperature,
                watsonx_api_key=watsonx_api_key,
                watsonx_project_id=watsonx_project_id,
                watsonx_url=watsonx_url,
                **kwargs
            )
        elif provider == "vllm":
            return LLMProviderFactory._create_vllm_llm(
                model_name=model_name,
                temperature=temperature,
                vllm_api_base=vllm_api_base,
                vllm_api_key=vllm_api_key,
                **kwargs
            )
        elif provider == "openai":
            return LLMProviderFactory._create_openai_llm(
                model_name=model_name,
                temperature=temperature,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_openai_llm(
        model_name: str,
        temperature: float,
        **kwargs
    ) -> ChatLiteLLM:
        """
        Create an OpenAI LLM instance via LiteLLM.
        
        Args:
            model_name: The name of the OpenAI model to use
            temperature: The temperature for response generation
            **kwargs: Additional parameters to pass to the LLM
            
        Returns:
            Configured ChatLiteLLM instance for OpenAI
        """
        return ChatLiteLLM(
            model=model_name,
            temperature=temperature,
            **kwargs
        )
    
    @staticmethod
    def _create_watsonx_llm(
        model_name: str,
        temperature: float,
        watsonx_api_key: Optional[str] = None,
        watsonx_project_id: Optional[str] = None,
        watsonx_url: Optional[str] = None,
        **kwargs
    ) -> ChatLiteLLM:
        """
        Create a Watsonx LLM instance via LiteLLM.
        
        Args:
            model_name: The name of the Watsonx model to use
            temperature: The temperature for response generation
            watsonx_api_key: Watsonx API key (required)
            watsonx_project_id: Watsonx project ID (required)
            watsonx_url: Watsonx URL (optional, defaults to US South region)
            **kwargs: Additional parameters to pass to the LLM
            
        Returns:
            Configured ChatLiteLLM instance for Watsonx
            
        Raises:
            ValueError: If required Watsonx credentials are missing
        """
        # Get credentials from environment or parameters
        api_key = watsonx_api_key or os.getenv("WATSONX_API_KEY")
        project_id = watsonx_project_id or os.getenv("WATSONX_PROJECT_ID")
        url = watsonx_url or os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        if not api_key or not project_id:
            raise ValueError(
                "Watsonx API key and project ID are required. "
                "Set WATSONX_API_KEY and WATSONX_PROJECT_ID environment variables "
                "or pass them as arguments."
            )
        
        # Set environment variables for LiteLLM
        os.environ["WATSONX_API_KEY"] = api_key
        os.environ["WATSONX_PROJECT_ID"] = project_id
        os.environ["WATSONX_URL"] = url
        
        # Use LiteLLM for Watsonx
        return ChatLiteLLM(
            model=f"watsonx/{model_name}",
            temperature=temperature,
            **kwargs
        )
    
    @staticmethod
    def _create_vllm_llm(
        model_name: str,
        temperature: float,
        vllm_api_base: Optional[str] = None,
        vllm_api_key: Optional[str] = None,
        **kwargs
    ) -> ChatLiteLLM:
        """
        Create a vLLM LLM instance via LiteLLM.
        
        Args:
            model_name: The name of the model to use
            temperature: The temperature for response generation
            vllm_api_base: vLLM API base URL (required)
            vllm_api_key: vLLM API key (optional, for authenticated endpoints)
            **kwargs: Additional parameters to pass to the LLM
            
        Returns:
            Configured ChatLiteLLM instance for vLLM
            
        Raises:
            ValueError: If vLLM API base URL is missing
        """
        # Get API base URL from environment or parameters
        api_base = vllm_api_base or os.getenv("VLLM_API_BASE")
        api_key = vllm_api_key or os.getenv("VLLM_API_KEY", "EMPTY")
        
        if not api_base:
            raise ValueError(
                "vLLM API base URL is required. "
                "Set VLLM_API_BASE environment variable or pass it as an argument."
            )
        
        # Use LiteLLM for vLLM with OpenAI-compatible API
        return ChatLiteLLM(
            model=f"openai/{model_name}",
            api_base=api_base,
            api_key=api_key,
            temperature=temperature,
            **kwargs
        )


def create_llm(
    provider: Optional[Literal["openai", "watsonx", "vllm"]] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs
) -> ChatLiteLLM:
    """
    Convenience function to create an LLM instance.
    All parameters can be loaded from environment variables if not provided.
    
    Environment Variables:
        LLM_PROVIDER: The LLM provider to use (default: "openai")
        MODEL_NAME: The model name (default: "gpt-4o-mini")
        TEMPERATURE: The temperature for response generation (default: 0.7)
        OPENAI_API_KEY: OpenAI API key (required for OpenAI provider)
        WATSONX_API_KEY: Watsonx API key (required for Watsonx provider)
        WATSONX_PROJECT_ID: Watsonx project ID (required for Watsonx provider)
        WATSONX_URL: Watsonx URL (default: "https://us-south.ml.cloud.ibm.com")
        VLLM_API_BASE: vLLM API base URL (required for vLLM provider)
        VLLM_API_KEY: vLLM API key (optional, for authenticated endpoints)
    
    Args:
        provider: The LLM provider to use (loaded from LLM_PROVIDER env var if not provided)
        model_name: The name of the model to use (loaded from MODEL_NAME env var if not provided)
        temperature: The temperature for response generation (loaded from TEMPERATURE env var if not provided)
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Configured ChatLiteLLM instance
    """
    return LLMProviderFactory.create_llm(
        provider=provider,
        model_name=model_name,
        temperature=temperature,
        **kwargs
    )

# Made with Bob
