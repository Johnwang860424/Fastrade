import controllers
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from . import valid

router = APIRouter()


class StockPriceResponse(BaseModel):
    date: str
    open: float
    min: float
    max: float
    close: float

    class Config:
        schema_extra = {
            "example": {"stock_price": [
                {
                    "date": "2023-02-01",
                    "open": 532,
                    "min": 522,
                    "max": 533,
                    "close": 530
                }
            ]}
        }


@router.get("/stockprice/", tags=["stock price"], responses={200: {"model": StockPriceResponse}})
async def get_stock_price(
        start_date: str = Query(None),
        end_date: str = Depends(valid.validate_date),
        symbol: str = Depends(valid.validate_symbol),
        price_type: str = Depends(valid.validate_price_type),
):
    """
    根據股票代碼、起始日期、結束日期、價格類型取得股價資料
    """
    stock_price = controllers.get_price(symbol, start_date, end_date[1], price_type)
    if stock_price:
        return {"stock_price": stock_price}
    elif not stock_price:
        return {"error": "No data found"}
    raise HTTPException(status_code=500, detail="Internal server error")
