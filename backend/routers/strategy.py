import controllers
from enum import Enum
from fastapi import APIRouter, Query, Depends, Path
from pydantic import BaseModel
from typing import Optional
from . import valid

router = APIRouter()

class BackTestingResponse(BaseModel):
    total_days: int
    total_trades: int
    num_wins: int
    num_losses: int
    win_rate: str
    roi: str
    total_profit: int
    average_risk_reward_ratio: float | str
    profit_factor: float | str
    
    class Config:
        schema_extra = {
            "example": {
                "backtesting_result": {
                    "total_days": 5704,
                    "total_trades": 325,
                    "num_wins": 125,
                    "num_losses": 200,
                    "win_rate": "38.46%",
                    "roi": "27.54%",
                    "total_profit": 27535,
                    "average_risk_reward_ratio": 1.75,
                    "profit_factor": 1.09
                    }
                }
            }

class CaseInsensitiveEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.name.lower() == value.lower():
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")
        
    def __getitem__(cls, name):
        return super().__getitem__(name.lower())

class ModelName(CaseInsensitiveEnum):
    ma = "MA"
    macd = "MACD"
    kd = "KD"

@router.get("/strategy/{strategy}", tags=["strategy"], responses={200: {"model": BackTestingResponse}})
async def strategy(
    strategy: ModelName = Path(description="進場策略：\n\nMA：[簡單移動平均線](https://rich01.com/what-is-moving-average-line)\n\nMACD：[平滑異同移動平均線指標](https://rich01.com/what-is-macd-indicator/)\n\nKD：[隨機指標](https://rich01.com/what-is-kd-indicator/)"),
    transaction_type: str = Query(..., regex="^(buy|sell)$",
                                  description="買賣類型\n\nbuy：做多\n\nsell：放空", example="buy"),
    short_term_ma: Optional[int] = Query(None, ge=5, le=2520, description="MA策略短期簡單移動平均線參數，最小值為5"),
    long_term_ma: Optional[int] = Query(None, ge=10, le=2520, description="MA策略長期簡單移動平均線參數，最小值為10"),
    short_term_macd: Optional[int] = Query(None, ge=5, le=2520, description="MACD策略短期指數移動平均線參數，最小值為5"),
    long_term_macd: Optional[int] = Query(None, ge=10, le=2520, description="MACD策略長期指數移動平均線參數，最小值為10"),
    signal_dif: Optional[int] = Query(None, ge=5, le=2520, description="MACD策略DIF指標的指數移動平均線參數，最小值為5"),
    recent_days: Optional[int] = Query(None, ge=5, le=2520, description="KD策略RSV指標天數，最小值為5"),
    k_d_argument: Optional[int] = Query(None, ge=3, le=2520, description="KD策略K及D的分母，最小值為3"),
    start_date: str = Depends(valid.validate_date),
    end_date: str = Depends(valid.validate_date),
    initial_capital: int = Query(..., ge=10, le=9999, description="初始資金(萬)，最小值為10"),
    symbol: str = Depends(valid.validate_symbol),
):
    """
    根據給定的進場策略、參數和交易類型，計算在給定時間區間內的交易策略表現\n
    做多時，採用黃金交叉時買進，死亡交叉時賣出；\n
    放空時，採用黃金交叉時賣出，死亡交叉時買進。\n
    黃金交叉：短期線由下往上穿越長期線 \n
    死亡交叉：短期線由上往下穿越長期線
    """
    if strategy == ModelName.ma:
        result = controllers.ma(transaction_type, short_term_ma, long_term_ma, start_date[0], end_date[1], initial_capital, symbol)
    elif strategy == ModelName.macd:
        result = controllers.macd(transaction_type, short_term_macd, long_term_macd, signal_dif, start_date[0], end_date[1], initial_capital, symbol)
    elif strategy == ModelName.kd:
        result = controllers.kd(transaction_type, recent_days, k_d_argument, start_date[0], end_date[1], initial_capital, symbol)
    if result:
        return {"backtesting_result": result}
    return {"error": "No data found"}