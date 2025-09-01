from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from .auth import hash_password, verify_password

SETTINGS_DOC_ID = "site_settings"

async def get_settings(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    doc = await db.settings.find_one({"_id": SETTINGS_DOC_ID})
    if not doc:
        return {
            "_id": SETTINGS_DOC_ID,
            "paypal_enabled": False,
            "paypal_mode": "sandbox",
            "paypal_client_id": None,
            "paypal_client_secret_set": False,
            "admin_password_hash": None,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
    return doc

async def get_public_settings(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    s = await get_settings(db)
    return {
        "paypal_enabled": bool(s.get("paypal_enabled")),
        "paypal_mode": s.get("paypal_mode", "sandbox"),
        "has_client_id": bool(s.get("paypal_client_id")),
    }

async def set_admin_password(db: AsyncIOMotorDatabase, new_password: str) -> None:
    hp = hash_password(new_password)
    await db.settings.update_one({"_id": SETTINGS_DOC_ID}, {"$set": {"admin_password_hash": hp, "updated_at": datetime.utcnow().isoformat() + "Z"}}, upsert=True)

async def check_admin_password(db: AsyncIOMotorDatabase, password: Optional[str]) -> bool:
    s = await get_settings(db)
    h = s.get("admin_password_hash")
    if not h:
        # Not initialized yet; allow if no password set
        return True
    return verify_password(password or "", h)

async def update_paypal_settings(db: AsyncIOMotorDatabase, payload: Dict[str, Any]) -> None:
    updates: Dict[str, Any] = {}
    for k in ["paypal_enabled", "paypal_mode", "paypal_client_id"]:
        if k in payload:
            updates[k] = payload[k]
    if "paypal_client_secret" in payload and payload["paypal_client_secret"]:
        # Store secret only as a flag in settings; save real value in a separate collection as needed
        await db.secrets.update_one({"name": "paypal_client_secret"}, {"$set": {"name": "paypal_client_secret", "value": payload["paypal_client_secret"], "updated_at": datetime.utcnow().isoformat() + "Z"}}, upsert=True)
        updates["paypal_client_secret_set"] = True
    if updates:
        updates["updated_at"] = datetime.utcnow().isoformat() + "Z"
        await db.settings.update_one({"_id": SETTINGS_DOC_ID}, {"$set": updates}, upsert=True)