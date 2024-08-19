"""Token validation module."""
from fastapi import Header
from fastapi import status
from fastapi.exceptions import HTTPException
from mongo_bot import const




async def verify_token(x_token: str = Header()):
    """
    Verify the X-Token header.


    Args:
        x_token (str): The value of the X-Token header.
    Raises:
        HTTPException: If the X-Token header is invalid.
    """
    if x_token != const.SERVICE_COM_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid X-Token header",
        )
