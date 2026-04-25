from pydantic import BaseModel
from typing import Optional


class StockData(BaseModel):
    ticker: str
    price: Optional[float]
    change_percent: Optional[float]
    market_cap: Optional[float]