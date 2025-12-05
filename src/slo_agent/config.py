"""
Configuration module for LLM settings
Handles all LLM-related configuration parameters.
"""

import os
from typing import Optional, Literal, cast
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """Configuration object for LLM settings."""
    
    # Core LLM settings
    provider: Optional[Literal["openai", "watsonx", "vllm"]] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    
    # Watsonx settings
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: Optional[str] = None
    
    # vLLM settings
    vllm_api_base: Optional[str] = None
    vllm_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Load configuration from environment variables if not provided."""
        # Load provider from environment
        if self.provider is None:
            provider_env = os.getenv("LLM_PROVIDER", "openai")
            if provider_env in ["openai", "watsonx", "vllm"]:
                self.provider = cast(Literal["openai", "watsonx", "vllm"], provider_env)
            else:
                self.provider = "openai"
        
        # Load model name from environment
        if self.model_name is None:
            self.model_name = os.getenv("MODEL_NAME", "mistralai/mistral-medium-2505")
        
        # Load temperature from environment
        if self.temperature is None:
            temp_env = os.getenv("TEMPERATURE")
            self.temperature = float(temp_env) if temp_env else 0.7
        
        # Load Watsonx settings from environment
        if self.watsonx_api_key is None:
            self.watsonx_api_key = os.getenv("WATSONX_API_KEY")
        if self.watsonx_project_id is None:
            self.watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
        if self.watsonx_url is None:
            self.watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        # Load vLLM settings from environment
        if self.vllm_api_base is None:
            self.vllm_api_base = os.getenv("VLLM_API_BASE")
        if self.vllm_api_key is None:
            self.vllm_api_key = os.getenv("VLLM_API_KEY", "EMPTY")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary for passing to LLM provider."""
        return {
            "provider": self.provider,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "watsonx_api_key": self.watsonx_api_key,
            "watsonx_project_id": self.watsonx_project_id,
            "watsonx_url": self.watsonx_url,
            "vllm_api_base": self.vllm_api_base,
            "vllm_api_key": self.vllm_api_key,
        }
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create configuration from environment variables only."""
        return cls()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"LLMConfig(provider={self.provider}, "
            f"model_name={self.model_name}, "
            f"temperature={self.temperature})"
        )


def create_llm_config(
    provider: Optional[Literal["openai", "watsonx", "vllm"]] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    watsonx_api_key: Optional[str] = None,
    watsonx_project_id: Optional[str] = None,
    watsonx_url: Optional[str] = None,
    vllm_api_base: Optional[str] = None,
    vllm_api_key: Optional[str] = None,
) -> LLMConfig:
    """
    Factory function to create LLM configuration.
    
    Args:
        provider: The LLM provider to use
        model_name: The model name
        temperature: The temperature setting
        watsonx_api_key: Watsonx API key
        watsonx_project_id: Watsonx project ID
        watsonx_url: Watsonx URL
        vllm_api_base: vLLM API base URL
        vllm_api_key: vLLM API key
        
    Returns:
        LLMConfig instance
    """
    return LLMConfig(
        provider=provider,
        model_name=model_name,
        temperature=temperature,
        watsonx_api_key=watsonx_api_key,
        watsonx_project_id=watsonx_project_id,
        watsonx_url=watsonx_url,
        vllm_api_base=vllm_api_base,
        vllm_api_key=vllm_api_key,
    )

# Made with Bob