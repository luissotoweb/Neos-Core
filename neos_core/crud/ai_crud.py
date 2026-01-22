from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from neos_core.database import models


def create_ai_interaction(
    db: Session,
    *,
    tenant_id: int,
    user_id: int,
    provider: str,
    model: Optional[str],
    operation: str,
    prompt: str,
    response: str,
    request_metadata: Optional[Dict[str, Any]] = None,
    response_metadata: Optional[Dict[str, Any]] = None,
) -> models.AIInteraction:
    interaction = models.AIInteraction(
        tenant_id=tenant_id,
        user_id=user_id,
        provider=provider,
        model=model,
        operation=operation,
        prompt=prompt,
        response=response,
        request_metadata=request_metadata,
        response_metadata=response_metadata,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
