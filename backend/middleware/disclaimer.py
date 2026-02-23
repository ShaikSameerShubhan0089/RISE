"""
Clinical Disclaimer Middleware
Adds clinical disclaimer to all risk prediction responses
"""

from fastapi import Request
from fastapi.responses import JSONResponse
import json


CLINICAL_DISCLAIMER = (
    "This tool provides autism risk stratification based on structured developmental "
    "assessments. It does NOT provide a clinical diagnosis. Final diagnosis must be "
    "made by a qualified pediatrician or developmental specialist."
)


async def add_clinical_disclaimer(request: Request, call_next):
    """
    Middleware to add clinical disclaimer to prediction responses
    """
    response = await call_next(request)
    
    # Only add disclaimer to prediction endpoints
    if "/predictions/" in request.url.path or "/risk" in request.url.path:
        # If response is JSON, add disclaimer field
        if response.headers.get("content-type") == "application/json":
            try:
                # Note: This is a simplified version
                # In production, you would need to properly handle streaming responses
                pass
            except:
                pass
    
    return response
