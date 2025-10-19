"""
Final working authentication module
src/shopcart_service/core/auth.py
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from uuid import UUID

# Define the security scheme ONCE - THIS creates the lock icon!
api_key_header = APIKeyHeader(
    name="X-User-Uuid",
    description="User UUID provided by API Gateway after JWT verification",
    auto_error=True  # Automatically show as required in Swagger
)


class User(BaseModel):
    """Current authenticated user"""
    user_uuid: UUID


async def get_user_from_gateway(
    x_user_uuid: str = Depends(api_key_header)  # Use Depends, not Security
) -> User:
    """
    Extract authenticated user from API Gateway header.
    
    API Gateway should add X-User-Uuid header after verifying JWT token.
    This function validates the UUID format.
    """
    if not x_user_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        parsed_uuid = UUID(x_user_uuid)
        return User(user_uuid=parsed_uuid)
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid UUID format: {str(e)}"
        )