from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import aiosqlite
from datetime import datetime
from app.database import get_db

router = APIRouter()

class FeedbackData(BaseModel):
    item_id: str
    actual_spoil_at: str

@router.post("")
async def record_feedback(data: FeedbackData, db: aiosqlite.Connection = Depends(get_db)):
    # 1. Look up latest prediction for this item
    async with db.execute(
        "SELECT predicted_spoil_by FROM predictions WHERE item_id = ? ORDER BY predicted_at DESC LIMIT 1",
        (data.item_id,)
    ) as cursor:
        pred = await cursor.fetchone()
    
    if not pred:
        raise HTTPException(status_code=404, detail="No prediction history found for this item")
    
    predicted_spoil_by_str = pred["predicted_spoil_by"]
    
    # 2. Compute error_hours = (actual_spoil_at - predicted_spoil_by)
    try:
        actual_dt = datetime.fromisoformat(data.actual_spoil_at)
        predicted_dt = datetime.fromisoformat(predicted_spoil_by_str)
        error_hours = (actual_dt - predicted_dt).total_seconds() / 3600.0
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    
    # 3. Record feedback and deactivate item
    now_str = datetime.now().isoformat()
    
    # Use a transaction-like approach (manual since we are using aiosqlite directly)
    await db.execute(
        """
        INSERT INTO feedback (item_id, submitted_at, actual_spoil_at, predicted_spoil_at, error_hours)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data.item_id, now_str, data.actual_spoil_at, predicted_spoil_by_str, error_hours)
    )
    
    await db.execute(
        "UPDATE food_items SET is_active = 0 WHERE item_id = ?",
        (data.item_id,)
    )
    
    await db.commit()
    
    return {
        "status": "recorded",
        "error_hours": round(error_hours, 2)
    }
