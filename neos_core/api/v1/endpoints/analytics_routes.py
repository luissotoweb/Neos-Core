"""
Endpoints de analíticas simples para demanda y anomalías.
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.schemas.analytics_schema import (
    BasicAnomaliesResponse,
    DemandProductHistory,
)
from neos_core.security.security_deps import get_current_user
from neos_core.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def check_analytics_permission(current_user: User = Depends(get_current_user)):
    allowed_roles = ["admin", "superadmin"]
    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado"
        )
    return current_user


@router.get("/demand-simple", response_model=List[DemandProductHistory])
def get_simple_demand(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_analytics_permission)
):
    return analytics_service.get_simple_demand_history(
        db=db,
        tenant_id=current_user.tenant_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/anomalies", response_model=BasicAnomaliesResponse)
def get_basic_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_analytics_permission)
):
    return analytics_service.get_basic_anomalies(
        db=db,
        tenant_id=current_user.tenant_id
    )
