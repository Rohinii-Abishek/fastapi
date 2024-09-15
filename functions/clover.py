import requests
from fastapi import HTTPException

CLOVER_API_URL = "https://sandbox.dev.clover.com/v3/merchants/TJGQ6YZ6M1271/orders"
CLOVER_API_KEY = "0ecfeebd-8bae-e6df-e58a-38b999430b7a"

headers = {
    "Authorization": f"Bearer {CLOVER_API_KEY}"
}

def fetch_order(order_id: str):
    url = f"{CLOVER_API_URL}/{order_id}?expand=lineItems"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order: {e}")

def create_line_item(order_id: str, line_item_payload: dict):
    url = f"{CLOVER_API_URL}/{order_id}/line_items"
    try:
        response = requests.post(url, json=line_item_payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating line item: {e}, Payload: {line_item_payload}")
        raise HTTPException(status_code=500, detail=f"Error creating line item: {e}")

def fetch_orders_with_filter(title: str = None):
    url = f"{CLOVER_API_URL}?filter=title={title}&expand=lineItems" if title else CLOVER_API_URL
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from Clover API: {e}")