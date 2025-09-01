from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from .auth import hash_password, verify_password, create_access_token
from .utils import now_iso, str_uuid

async def signup(db: AsyncIOMotorDatabase, username: str, email: str, password: str) -> Dict[str, Any]:
    if await db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return {"success": False, "message": "User exists"}
    user = {
        "id": str_uuid(),
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "first_name": "",
        "last_name": "",
        "phone": "",
        "company": "",
        "is_premium": False,
        "plan": {"plan_type": "free", "billing_cycle": "monthly", "features": {}},
        "last_login": None,
        "date_joined": now_iso(),
        "email_verified": False,
    }
    await db.users.insert_one(user)
    token = create_access_token({"sub": user["id"]})
    return {"success": True, "token": token, "user": user}

async def create_reset_token(db: AsyncIOMotorDatabase, email: str) -> Dict[str, Any]:
    user = await db.users.find_one({"email": email})
    if not user:
        return {"success": False, "message": "Email not found"}
    tok = str_uuid()
    await db.password_resets.insert_one({"token": tok, "user_id": user["id"], "email": email, "created_at": now_iso(), "used": False})
    return {"success": True, "token": tok}

async def reset_password(db: AsyncIOMotorDatabase, token: str, new_password: str) -> Dict[str, Any]:
    rec = await db.password_resets.find_one({"token": token, "used": False})
    if not rec:
        return {"success": False, "message": "Invalid token"}
    await db.users.update_one({"id": rec["user_id"]}, {"$set": {"password_hash": hash_password(new_password)}})
    await db.password_resets.update_one({"token": token}, {"$set": {"used": True, "used_at": now_iso()}})
    return {"success": True}

async def create_verify_token(db: AsyncIOMotorDatabase, user_id: str) -> str:
    tok = str_uuid()
    await db.email_verifications.insert_one({"token": tok, "user_id": user_id, "created_at": now_iso(), "used": False})
    return tok

async def verify_email(db: AsyncIOMotorDatabase, token: str) -> Dict[str, Any]:
    rec = await db.email_verifications.find_one({"token": token, "used": False})
    if not rec:
        return {"success": False, "message": "Invalid token"}
    await db.users.update_one({"id": rec["user_id"]}, {"$set": {"email_verified": True}})
    await db.email_verifications.update_one({"token": token}, {"$set": {"used": True, "used_at": now_iso()}})
    return {"success": True}