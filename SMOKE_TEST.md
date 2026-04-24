# Spoiler Alert Backend Smoke Test

Follow these steps in order to test the full happy path of the application.
Assumes the server is running at `http://localhost:8000`.

### 1. Root / Health Check
```bash
curl -X GET http://localhost:8000/
```

### 2. Register a Device
```bash
curl -X POST http://localhost:8000/register-device \
     -H "Content-Type: application/json" \
     -d '{"device_id": "DEV_001", "user_id": "USER_123"}'
```

### 3. Add a Food Item
```bash
curl -X POST http://localhost:8000/add-food-item \
     -H "Content-Type: application/json" \
     -d '{"device_id": "DEV_001", "label": "Milk", "food_category": "dairy"}'
```
*Take note of the `"item_id"` in the response.*

### 4. Ingest an Image
*(Replace `path/to/image.jpg` with a real image file)*
```bash
curl -X POST http://localhost:8000/ingest \
     -F "device_id=DEV_001" \
     -F "timestamp=2024-04-24T12:00:00" \
     -F "image=@path/to/image.jpg"
```

### 5. Get Active Items (List)
```bash
curl -X GET http://localhost:8000/items/DEV_001
```

### 6. Get Item History
```bash
curl -X GET http://localhost:8000/item-history/<ITEM_ID>
```

### 7. Record Feedback (Item Spoiled)
```bash
curl -X POST http://localhost:8000/feedback \
     -H "Content-Type: application/json" \
     -d '{"item_id": "<ITEM_ID>", "actual_spoil_at": "2024-04-25T12:00:00"}'
```
