from fastapi import Query, HTTPException, Request
import datetime


def validate_symbol(
    symbol: str = Query(..., min_length=4, max_length=4, description="股票代號，例如 '2330'"),
):
    try:
        symbol_int = int(symbol)
        if len(symbol) != 4:
            raise ValueError("Symbol must be a 4-digit integer")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    return symbol_int


def validate_date(
    start_date: str = Query(..., description="開始日期，格式為 'YYYY-MM-DD'"),
    end_date: str = Query(..., description="結束日期，格式為 'YYYY-MM-DD'"),
    request: Request = None,
):
    try:
        start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if start_datetime > end_datetime:
            raise HTTPException(
                status_code=400, detail="start_date cannot be greater than end_date"
            )
        elif start_datetime < datetime.datetime.strptime("2000-01-01", "%Y-%m-%d"):
            raise HTTPException(
                status_code=400, detail="start_date cannot be earlier than 2000-01-01"
            )
        elif end_datetime > datetime.datetime.today():
            raise HTTPException(
                status_code=400, detail="end_date cannot be later than today"
            )
        elif (
            request.url.path == "/strategy/"
            and (end_datetime - start_datetime).days < 30
        ):
            raise HTTPException(
                status_code=400,
                detail="end_date must be at least 30 days after start_date",
            )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    return start_date, end_date


def validate_price_type(
    price_type: str = Query(
        ...,
        regex="^(origin|adjust)$",
        description="價格類型：\n\norigin：原始價格\n\nadjust：還原價格",
    ),
):
    return price_type
