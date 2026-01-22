"""
Schemas para reportes y analíticas básicas.
"""
from datetime import date
from decimal import Decimal
from typing import List

from pydantic import BaseModel


class DemandHistoryEntry(BaseModel):
    date: date
    total_quantity: Decimal
    total_sales: Decimal


class DemandProductHistory(BaseModel):
    product_id: int
    product_name: str
    total_quantity: Decimal
    total_sales: Decimal
    history: List[DemandHistoryEntry]


class NegativeMarginProduct(BaseModel):
    product_id: int
    product_name: str
    cost: Decimal
    price: Decimal
    margin: Decimal


class LowStockProduct(BaseModel):
    product_id: int
    product_name: str
    stock: Decimal
    min_stock: Decimal


class SaleDiscrepancy(BaseModel):
    sale_id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    difference: Decimal


class BasicAnomaliesResponse(BaseModel):
    negative_margins: List[NegativeMarginProduct]
    low_stock: List[LowStockProduct]
    sale_discrepancies: List[SaleDiscrepancy]
