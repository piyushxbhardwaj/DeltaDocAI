import os
from typing import Optional
from src.rag.base import BaseLLM, LLMResponse
from src.observability.logger import logger

class GeminiProvider(BaseLLM):
    """Google Gemini 2.5 Flash LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.startswith("mock"):
            logger.warning("No valid GEMINI_API_KEY provided. Gemini LLM operating in simulated mock mode.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini client initialized with model '{self.model_name}'.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini SDK ({e}). Running in fallback mode.")
            self.client = None

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        full_prompt = f"{system_prompt}\n\nUser Question:\n{prompt}" if system_prompt else prompt

        if self.client:
            try:
                response = self.client.generate_content(full_prompt)
                text = response.text if hasattr(response, "text") else str(response)
                prompt_tokens = len(full_prompt.split()) * 2
                completion_tokens = len(text.split()) * 2
                cost = (prompt_tokens * 0.0000005) + (completion_tokens * 0.0000015)
                
                return LLMResponse(
                    text=text,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    estimated_cost_usd=round(cost, 6),
                    model=self.model_name
                )
            except Exception as e:
                logger.error(f"Gemini API error ({e}). Returning fallback response.")

        # Fallback simulation for offline testing
        fallback_text = (
            "Based on the retrieved context:\n"
            "• **Changes:** Valve V-102 was removed in Revision B on Page 1.\n"
            "• **Modifications:** Instrument 26-PIT-9055 pressure reading updated from 100 PSI to 150 PSI [Delta Report, Page 1].\n"
            "• **Additions:** Pipeline 6\"-CS-150 added [Revision B, Page 1]."
        )
        return LLMResponse(
            text=fallback_text,
            prompt_tokens=len(full_prompt.split()),
            completion_tokens=len(fallback_text.split()),
            estimated_cost_usd=0.00005,
            model=f"{self.model_name} (Simulated)"
        )


class OpenAIProvider(BaseLLM):
    """OpenAI GPT-4o / GPT-3.5 provider for swappability."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.startswith("mock"):
            logger.warning("No valid OPENAI_API_KEY provided. OpenAI provider in mock mode.")
            return
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized with model '{self.model_name}'.")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if self.client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                res = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages
                )
                text = res.choices[0].message.content or ""
                p_tokens = res.usage.prompt_tokens if res.usage else 0
                c_tokens = res.usage.completion_tokens if res.usage else 0
                cost = (p_tokens * 0.000005) + (c_tokens * 0.000015)

                return LLMResponse(
                    text=text,
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    estimated_cost_usd=round(cost, 6),
                    model=self.model_name
                )
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")

        # Fallback simulation
        return LLMResponse(
            text="OpenAI Provider (Simulated Response based on retrieved context).",
            prompt_tokens=50,
            completion_tokens=20,
            estimated_cost_usd=0.0001,
            model=f"{self.model_name} (Simulated)"
        )


def get_llm_provider(provider_type: str = "gemini") -> BaseLLM:
    """Factory function for LLM provider dependency injection."""
    ptype = (provider_type or os.getenv("LLM_PROVIDER", "gemini")).lower()
    if ptype == "openai":
        return OpenAIProvider()
    return GeminiProvider()
