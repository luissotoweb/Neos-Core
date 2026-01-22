"""
Cliente de integración con proveedores de IA (OpenAI/Anthropic).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib import request
from urllib.error import HTTPError
import json
import os
import base64


@dataclass
class AIClientSettings:
    provider: str
    api_key: str
    model: str
    base_url: Optional[str] = None
    timeout_s: int = 30


class AIClient:
    def __init__(self, settings: AIClientSettings):
        self.settings = settings
        self.provider = settings.provider.lower()

    @classmethod
    def from_env(cls) -> "AIClient":
        provider = os.getenv("AI_PROVIDER", "openai")
        provider_lower = provider.lower()
        if provider_lower == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", os.getenv("AI_MODEL", "gpt-4o-mini"))
            base_url = os.getenv("OPENAI_BASE_URL", os.getenv("AI_BASE_URL"))
        elif provider_lower == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("ANTHROPIC_MODEL", os.getenv("AI_MODEL", "claude-3-haiku-20240307"))
            base_url = os.getenv("ANTHROPIC_BASE_URL", os.getenv("AI_BASE_URL"))
        else:
            raise ValueError(f"Proveedor de IA no soportado: {provider}")

        if not api_key:
            raise ValueError(f"API key no configurada para proveedor {provider}")

        settings = AIClientSettings(
            provider=provider_lower,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
        return cls(settings)

    def generate_text(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.2,
        max_tokens: int = 800,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.provider == "openai":
            return self._openai_chat(messages, temperature, max_tokens, image_bytes, image_mime_type)
        if self.provider == "anthropic":
            return self._anthropic_messages(messages, temperature, max_tokens, image_bytes, image_mime_type)
        raise ValueError(f"Proveedor de IA no soportado: {self.provider}")

    def _openai_chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
        image_bytes: Optional[bytes],
        image_mime_type: Optional[str],
    ) -> Dict[str, Any]:
        url = self.settings.base_url or "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload_messages = list(messages)
        if image_bytes:
            image_content = self._encode_image_for_openai(image_bytes, image_mime_type)
            if payload_messages:
                payload_messages[-1] = {
                    **payload_messages[-1],
                    "content": [
                        {"type": "text", "text": payload_messages[-1]["content"]},
                        image_content,
                    ],
                }

        payload = {
            "model": self.settings.model,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = self._post_json(url, headers, payload)
        message = response.get("choices", [{}])[0].get("message", {})
        return {
            "text": message.get("content", ""),
            "raw": response,
        }

    def _anthropic_messages(
        self,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
        image_bytes: Optional[bytes],
        image_mime_type: Optional[str],
    ) -> Dict[str, Any]:
        url = self.settings.base_url or "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.settings.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        system_content = None
        payload_messages = []
        for message in messages:
            if message.get("role") == "system":
                system_content = message.get("content")
            else:
                payload_messages.append(message)

        if image_bytes:
            image_content = self._encode_image_for_anthropic(image_bytes, image_mime_type)
            if payload_messages:
                payload_messages[-1] = {
                    **payload_messages[-1],
                    "content": [
                        {"type": "text", "text": payload_messages[-1]["content"]},
                        image_content,
                    ],
                }

        payload = {
            "model": self.settings.model,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_content:
            payload["system"] = system_content
        response = self._post_json(url, headers, payload)
        text_blocks = response.get("content", [])
        text = "".join(block.get("text", "") for block in text_blocks)
        return {
            "text": text,
            "raw": response,
        }

    def _post_json(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.settings.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as exc:
            error_payload = exc.read().decode("utf-8")
            raise RuntimeError(
                f"Error llamando proveedor de IA: {exc.code} {exc.reason} - {error_payload}"
            ) from exc

    @staticmethod
    def _encode_image_for_openai(image_bytes: bytes, image_mime_type: Optional[str]) -> Dict[str, Any]:
        mime_type = image_mime_type or "image/png"
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
        }

    @staticmethod
    def _encode_image_for_anthropic(image_bytes: bytes, image_mime_type: Optional[str]) -> Dict[str, Any]:
        mime_type = image_mime_type or "image/png"
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime_type,
                "data": encoded,
            },
        }
