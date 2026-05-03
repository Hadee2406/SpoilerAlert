from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/status")
def get_status():
    return {
        "status": random.choice(["Fresh", "Attention", "Spoiling", "Spoiled"]),
        "confidence": round(random.uniform(0.7, 0.95), 2)
    }


@router.get("/trend")
def get_trend():
    return {
        "points": [
            {"day": "Mon", "value": 1},
            {"day": "Tue", "value": 3},
            {"day": "Wed", "value": 0},
            {"day": "Thu", "value": 1},
            {"day": "Fri", "value": 2},
            {"day": "Sat", "value": 3},
            {"day": "Sun", "value": 4},
        ]
    }


@router.get("/notifications")
def get_notifications():
    return {
        "notifications": [
            {
                "id": "1",
                "title": "Reminder",
                "message": "Check your vegetables",
                "type": "warning",
                "timestamp": str(datetime.now())
            }
        ]
    }


@router.get("/device-status")
def get_device_status():
    return {
        "is_online": True,
        "last_seen": str(datetime.now())
    }