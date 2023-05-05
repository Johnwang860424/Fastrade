import json
import redis


def filter_type(stock, type_filter):
    if "type" in stock.keys():
        if stock["type"] == type_filter:
            stock.pop("type")
            return stock


def lambda_handler(event, context):
    # Connect to Elasticache Redis using the redis-py library
    r = redis.Redis(
        host="stocklist-001.cfrhde.0001.apne1.cache.amazonaws.com", port=6379, db=0
    )

    # TODO implement
    records = event["Records"][0]["body"]
    records = json.loads(records)

    listed_stock = list(filter(lambda stock: filter_type(stock, "1"), records))
    OTC_stock = list(filter(lambda stock: filter_type(stock, "2"), records))
    all_stock = listed_stock + OTC_stock

    r.set("listed_stock_list", json.dumps(listed_stock))
    r.set("OTC_stock_list", json.dumps(OTC_stock))
    r.set("all_stock_list", json.dumps(all_stock))

    return {"statusCode": 200, "body": json.dumps("Saved successfully")}
