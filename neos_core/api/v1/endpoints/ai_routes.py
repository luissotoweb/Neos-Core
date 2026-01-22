from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database import models
from neos_core.database.models import User
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.ai_schema import CatalogProductResponse, NLPSQLRequest, NLPSQLResponse
from neos_core.schemas.expense_schema import ExpenseSuggestionRequest, ExpenseSuggestionResponse
from neos_core.services.ai_client import AIClient
from neos_core.crud import create_ai_interaction

router = APIRouter(prefix="/ai")


def _extract_json_payload(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    return {}


def _validate_tenant_filter(sql: str, tenant_id: int) -> bool:
    pattern = rf"(\btenant_id\b|\b\w+\.tenant_id\b)\s*=\s*{tenant_id}\b"
    return re.search(pattern, sql, re.IGNORECASE) is not None


@router.post("/catalog-product", response_model=CatalogProductResponse)
def catalog_product(
    image: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Catalogación de producto usando IA.

    Recibe una imagen y metadata opcional (JSON en string).
    """
    try:
        client = AIClient.from_env()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    metadata_payload: Dict[str, Any] = {}
    if metadata:
        try:
            metadata_payload = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="metadata debe ser JSON válido",
            ) from exc

    image_bytes = image.file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Imagen vacía")

    system_prompt = (
        "Eres un asistente experto en catalogación de productos. "
        "Devuelve un JSON con llaves: name, description, category, sku, barcode, tags, attributes. "
        "Usa tags como lista y attributes como objeto con claves libres."
    )
    user_prompt = f"Metadata proporcionada: {json.dumps(metadata_payload, ensure_ascii=False)}"

    result = client.generate_text(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=600,
        image_bytes=image_bytes,
        image_mime_type=image.content_type,
    )

    response_text = result.get("text", "")
    catalog_payload = _extract_json_payload(response_text)

    create_ai_interaction(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        provider=client.provider,
        model=client.settings.model,
        operation="catalog_product",
        prompt=f"{system_prompt}\n{user_prompt}",
        response=response_text,
        request_metadata={
            "filename": image.filename,
            "content_type": image.content_type,
            "metadata": metadata_payload,
        },
        response_metadata={
            "catalog_keys": list(catalog_payload.keys()) if catalog_payload else [],
        },
    )

    return CatalogProductResponse(
        provider=client.provider,
        model=client.settings.model,
        catalog=catalog_payload,
        raw_response=response_text,
    )


@router.post("/nlp-to-sql", response_model=NLPSQLResponse)
def nlp_to_sql(
    payload: NLPSQLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convierte una pregunta en SQL (solo SELECT) con aislamiento por tenant.
    """
    try:
        client = AIClient.from_env()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    system_prompt = (
        "Eres un asistente que convierte lenguaje natural a SQL. "
        "Responde en JSON con llaves sql y notes. "
        "Solo se permiten consultas SELECT. "
        f"Siempre filtra por tenant_id = {current_user.tenant_id}. "
        f"Usa dialecto {payload.dialect}."
    )
    user_prompt = payload.question
    if payload.schema_context:
        user_prompt += f"\n\nContexto de esquema:\n{payload.schema_context}"

    result = client.generate_text(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=400,
    )

    response_text = result.get("text", "")
    response_payload = _extract_json_payload(response_text)
    sql = response_payload.get("sql") or response_text
    notes = response_payload.get("notes")

    sql_clean = sql.strip()
    if not sql_clean.lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La respuesta generada no es un SELECT válido",
        )

    has_tenant_filter = _validate_tenant_filter(sql_clean, current_user.tenant_id)
    if not has_tenant_filter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La consulta generada no cumple aislamiento por tenant",
        )

    create_ai_interaction(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        provider=client.provider,
        model=client.settings.model,
        operation="nlp_to_sql",
        prompt=f"{system_prompt}\n{user_prompt}",
        response=response_text,
        request_metadata={
            "question": payload.question,
            "schema_context": payload.schema_context,
            "dialect": payload.dialect,
        },
        response_metadata={
            "validated": True,
            "has_tenant_filter": has_tenant_filter,
        },
    )

    return NLPSQLResponse(
        provider=client.provider,
        model=client.settings.model,
        sql=sql_clean,
        notes=notes,
        raw_response=response_text,
    )


@router.post("/expense-suggest", response_model=ExpenseSuggestionResponse)
def suggest_expense_account(
    payload: ExpenseSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sugiere una cuenta contable para un gasto usando IA.
    """
    try:
        client = AIClient.from_env()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    system_prompt = (
        "Eres un asistente contable. "
        "Devuelve un JSON con la llave account_code para la cuenta sugerida. "
        "Responde solo con JSON."
    )
    user_prompt = (
        f"Descripción del gasto: {payload.description}. "
        f"Monto: {payload.amount}."
    )

    result = client.generate_text(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=200,
    )

    response_text = result.get("text", "")
    response_payload = _extract_json_payload(response_text)
    suggested_account = (
        response_payload.get("account_code")
        or response_payload.get("suggested_account")
        or response_text.strip()
    )

    expense = models.Expense(
        tenant_id=current_user.tenant_id,
        description=payload.description,
        amount=payload.amount,
        suggested_account=suggested_account,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    create_ai_interaction(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        provider=client.provider,
        model=client.settings.model,
        operation="expense_suggest_account",
        prompt=f"{system_prompt}\n{user_prompt}",
        response=response_text,
        request_metadata={
            "description": payload.description,
            "amount": str(payload.amount),
        },
        response_metadata={
            "suggested_account": suggested_account,
            "expense_id": expense.id,
        },
    )

    return ExpenseSuggestionResponse(
        provider=client.provider,
        model=client.settings.model,
        suggested_account=suggested_account,
        expense=expense,
        raw_response=response_text,
    )
