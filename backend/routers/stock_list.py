import controllers
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class StockListResponse(BaseModel):
    symbol: str
    name: str

    class Config:
        schema_extra = {
            "example": {
                "stock_list": [
                    {
                        "symbol": "1101",
                        "name": "台泥",
                    }
                ]
            }
        }


@router.get("/stocklist/", tags=["stock list"], responses={200: {"model": StockListResponse}})
async def get_stock_list(stocktype: str = Query(None, description="股票清單類型：\n\n空白：上市櫃股票清單\n\nlisted：上市股票清單\n\nOTC：上櫃股票清單", regex="^(listed|OTC)$")):
    """
    根據股票類型取得股票清單
    """
    stock_list = controllers.get_stock_list(stocktype if stocktype else None)
    if stock_list:
        return {"stock_list": stock_list}
    return {"error": "Could not fetch stocks"}
