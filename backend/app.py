from fastapi import FastAPI
import uvicorn
import routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.stock_list.router)
app.include_router(routers.stock_price.router)

app.include_router(routers.strategy.router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)