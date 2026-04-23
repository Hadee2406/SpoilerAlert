import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging
import aiosqlite
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIREBASE_ENABLED = False

try:
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        FIREBASE_ENABLED = True
        logger.info("Firebase Admin SDK initialized successfully.")
    else:
        logger.warning(f"Firebase credentials not found at {settings.FIREBASE_CREDENTIALS_PATH}. Notifications disabled.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

async def send_spoilage_notification(
    device_id: str, 
    label: str, 
    hours: float, 
    item_id: str, 
    spoilage_score: float,
    db: aiosqlite.Connection
):
    """
    Sends a push notification to the registered device using FCM.
    Fetches the fcm_token from the database.
    """
    # 1. Look up the device's FCM token
    async with db.execute("SELECT fcm_token FROM devices WHERE device_id = ?", (device_id,)) as cursor:
        row = await cursor.fetchone()
    
    if not row or not row["fcm_token"]:
        logger.warning(f"No FCM token found for device {device_id}. Cannot send notification.")
        return

    fcm_token = row["fcm_token"]

    # 2. Handle disabled Firebase (development/missing config)
    if not FIREBASE_ENABLED:
        print("\n" + "="*50)
        print("FIREBASE NOTIFICATION (MOCK):")
        print(f"Token: {fcm_token}")
        print(f"Title: ⚠️ Spoilage Alert")
        print(f"Body: {label} may spoil in ~{hours:.0f} hours.")
        print(f"Data: item_id={item_id}, score={spoilage_score}")
        print("="*50 + "\n")
        return

    # 3. Build and send the real message
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="⚠️ Spoilage Alert",
                body=f"{label} may spoil in ~{hours:.0f} hours."
            ),
            data={
                "item_id": str(item_id),
                "spoilage_score": f"{spoilage_score:.2f}"
            },
            token=fcm_token
        )
        
        message_id = messaging.send(message)
        logger.info(f"Successfully sent Firebase notification. Message ID: {message_id}")
        
    except Exception as e:
        logger.error(f"Firebase Messaging error for device {device_id}: {str(e)}")
