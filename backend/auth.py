from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import supabase


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        return response.user

    except HTTPException:
        raise

    except Exception as e:
        print("AUTH ERROR:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )