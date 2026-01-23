from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib import request
from urllib.error import HTTPError

from sqlalchemy.orm import Session

from neos_core.database.models import Product, ProductEmbedding


@dataclass
class EmbeddingSettings:
    provider: str
    model: str
    base_url: str
    api_key: Optional[str] = None
    timeout_s: int = 30


class EmbeddingClient:
    def __init__(self, settings: EmbeddingSettings):
        self.settings = settings
        self.provider = settings.provider.lower()

    @classmethod
    def from_env(cls) -> "EmbeddingClient":
        provider = os.getenv("EMBEDDINGS_PROVIDER", os.getenv("AI_PROVIDER", "openai")).lower()
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY no configurada para embeddings")
            model = os.getenv("OPENAI_EMBEDDINGS_MODEL", os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small"))
            base_url = os.getenv("OPENAI_EMBEDDINGS_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/embeddings"))
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY no configurada para embeddings")
            model = os.getenv("ANTHROPIC_EMBEDDINGS_MODEL", os.getenv("EMBEDDINGS_MODEL", "claude-3-haiku-20240307"))
            base_url = os.getenv("ANTHROPIC_EMBEDDINGS_BASE_URL", os.getenv("EMBEDDINGS_BASE_URL", "https://api.anthropic.com/v1/embeddings"))
        elif provider == "ollama":
            api_key = None
            model = os.getenv("OLLAMA_EMBEDDINGS_MODEL", os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text"))
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
        else:
            raise ValueError(f"Proveedor de embeddings no soportado: {provider}")

        settings = EmbeddingSettings(
            provider=provider,
            model=model,
            base_url=base_url,
            api_key=api_key,
        )
        return cls(settings)

    def embed_text(self, text: str) -> List[float]:
        if self.provider == "openai":
            return self._openai_embeddings(text)
        if self.provider == "anthropic":
            return self._anthropic_embeddings(text)
        if self.provider == "ollama":
            return self._ollama_embeddings(text)
        raise ValueError(f"Proveedor de embeddings no soportado: {self.provider}")

    def _openai_embeddings(self, text: str) -> List[float]:
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.settings.model, "input": text}
        response = self._post_json(self.settings.base_url, headers, payload)
        return response.get("data", [{}])[0].get("embedding", [])

    def _anthropic_embeddings(self, text: str) -> List[float]:
        headers = {
            "x-api-key": self.settings.api_key or "",
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {"model": self.settings.model, "input": text}
        response = self._post_json(self.settings.base_url, headers, payload)
        return response.get("data", [{}])[0].get("embedding", [])

    def _ollama_embeddings(self, text: str) -> List[float]:
        headers = {"Content-Type": "application/json"}
        payload = {"model": self.settings.model, "prompt": text}
        response = self._post_json(self.settings.base_url, headers, payload)
        return response.get("embedding", [])

    def _post_json(self, url: str, headers: dict, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.settings.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as exc:
            error_payload = exc.read().decode("utf-8")
            raise RuntimeError(
                f"Error llamando proveedor de embeddings: {exc.code} {exc.reason} - {error_payload}"
            ) from exc


def build_product_embedding_text(product: Product) -> str:
    attributes_text = ""
    if product.attributes:
        attributes_text = json.dumps(product.attributes, ensure_ascii=False, sort_keys=True)
    parts = [product.name]
    if product.description:
        parts.append(product.description)
    if attributes_text:
        parts.append(f"Atributos: {attributes_text}")
    return "\n\n".join(part.strip() for part in parts if part and str(part).strip())


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _ensure_embeddings(
    db: Session,
    tenant_id: int,
    products: Iterable[Product],
    client: EmbeddingClient,
) -> dict[int, ProductEmbedding]:
    product_list = list(products)
    product_ids = [product.id for product in product_list]
    embeddings = {}
    if product_ids:
        embeddings = {
            embedding.product_id: embedding
            for embedding in db.query(ProductEmbedding)
            .filter(ProductEmbedding.tenant_id == tenant_id, ProductEmbedding.product_id.in_(product_ids))
            .all()
        }

    updated = False
    for product in product_list:
        text = build_product_embedding_text(product)
        content_hash = _hash_text(text)
        existing = embeddings.get(product.id)
        if existing and existing.content_hash == content_hash:
            continue
        embedding_vector = client.embed_text(text)
        if existing:
            existing.embedding = embedding_vector
            existing.content_hash = content_hash
            existing.provider = client.provider
            existing.model = client.settings.model
        else:
            new_embedding = ProductEmbedding(
                tenant_id=tenant_id,
                product_id=product.id,
                provider=client.provider,
                model=client.settings.model,
                content_hash=content_hash,
                embedding=embedding_vector,
            )
            db.add(new_embedding)
            embeddings[product.id] = new_embedding
        updated = True

    if updated:
        db.commit()

    return embeddings


def semantic_search_products(
    db: Session,
    tenant_id: int,
    query: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Tuple[Product, float]]:
    products = (
        db.query(Product)
        .filter(Product.tenant_id == tenant_id)
        .all()
    )
    if not products:
        return []

    client = EmbeddingClient.from_env()
    embeddings = _ensure_embeddings(db, tenant_id, products, client)
    query_vector = client.embed_text(query)

    scored_products: List[Tuple[Product, float]] = []
    for product in products:
        embedding = embeddings.get(product.id)
        vector = embedding.embedding if embedding else None
        score = _cosine_similarity(query_vector, vector or [])
        scored_products.append((product, score))

    scored_products.sort(key=lambda item: item[1], reverse=True)
    return scored_products[skip: skip + limit]
