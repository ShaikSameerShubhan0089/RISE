"""
Audit Logging Middleware
Automatically logs all API requests to audit_logs table
"""

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import Callable
import sys
from pathlib import Path

# Add parent directory to path to import database and models
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal
import models


async def log_request(request: Request, call_next: Callable):
    """
    Middleware to log all API requests
    """
    # Get request details
    method = request.method
    path = request.url.path
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    # Read request body (if present)
    request_body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                request_body = body_bytes.decode("utf-8")
                # Redact sensitive fields
                try:
                    body_dict = json.loads(request_body)
                    if "password" in body_dict:
                        body_dict["password"] = "***REDACTED***"
                    request_body = json.dumps(body_dict)
                except:
                    pass
        except:
            pass
    
    # Process request
    response = await call_next(request)
    
    # Get user_id from request state (set by auth middleware during request processing)
    user_id = getattr(request.state, "user_id", None)
    
    # Log to database (in background)
    try:
        db = SessionLocal()
        
        log_entry = models.AuditLog(
            user_id=user_id,
            action=f"{method} {path}",
            entity_type=extract_entity_type(path),
            entity_id=extract_entity_id(path),
            request_method=method,
            request_path=path,
            request_body=request_body[:1000] if request_body else None,  # Limit size
            response_status=response.status_code,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None  # Limit size
        )
        
        db.add(log_entry)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Failed to log request: {e}")
    
    return response


def extract_entity_type(path: str) -> str:
    """Extract entity type from API path"""
    parts = path.strip("/").split("/")
    
    if len(parts) >= 2 and parts[0] == "api":
        entity = parts[1]
        
        # Map plural to singular
        entity_map = {
            "children": "child",
            "assessments": "assessment",
            "predictions": "prediction",
            "referrals": "referral",
            "interventions": "intervention",
            "users": "user"
        }
        
        return entity_map.get(entity, entity)
    
    return None


def extract_entity_id(path: str) -> int:
    """Extract entity ID from API path if present"""
    parts = path.strip("/").split("/")
    
    # Look for numeric ID in path
    for part in parts:
        if part.isdigit():
            return int(part)
    
    return None
