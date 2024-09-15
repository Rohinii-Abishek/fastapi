from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict
from functions.clover import fetch_order, create_line_item, fetch_orders_with_filter

app = FastAPI()


@app.get("/orders")
async def get_orders(filter: Optional[str] = Query(None)):
    title = filter.split('=')[1] if filter and filter.startswith("title=") else None
    data = fetch_orders_with_filter(title)
    formatted_data = {"data": []}
    item_counts = {}
    for order in data.get("elements", []):
        line_items = order.get("lineItems", {}).get("elements", [])
        for line_item in line_items:
            item_id = line_item.get("item", {}).get("id")
            if item_id:
                item_counts[item_id] = item_counts.get(item_id, 0) + 1
    for item_id, quantity in item_counts.items():
        formatted_data["data"].append({
            "id": item_id,
            "quantity": quantity
        })
    return formatted_data


@app.post("/orders/{order_id}/add-line-items")
async def add_line_items(order_id: str, payload: Dict):
    try:
        index = payload["index"]
        title = payload["title"]
        data = payload["data"]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field in payload: {e}")
    fetched_order = fetch_order(order_id)
    if not fetched_order:
        raise HTTPException(status_code=404, detail="Order not found")
    line_items_from_fetched_order = fetched_order.get("lineItems", {}).get("elements", [])
    existing_items = {item["item"]["id"]: item for item in line_items_from_fetched_order}
    orders_created = []
    for item in data:
        item_id = item.get("id")
        quantity = item.get("quantity", 1)
        name = existing_items.get(item_id, {}).get("name", "")
        price = existing_items.get(item_id, {}).get("price", 0)
        for _ in range(quantity):
            line_item_payload = {
                "item": {
                    "id": item_id
                },
                "printed": "false",
                "exchanged": "false",
                "refunded": "false",
                "refund": {
                    "transactionInfo": {
                        "isTokenBasedTx": "false",
                        "emergencyFlag": "false"
                    }
                },
                "isRevenue": "false",
                "name": name,
                "price": price
            }
            created_line_item = create_line_item(order_id, line_item_payload)
            orders_created.append(created_line_item)
    return {"message": "Line items added successfully", "orders": orders_created}
