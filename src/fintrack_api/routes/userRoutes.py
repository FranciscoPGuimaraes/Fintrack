from datetime import timedelta
from typing import Annotated, Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import authenticate_user, create_access_token, get_api_key, get_password_hash

from services.user import create_user, get_all_users
from models.userModels import UserInDB, UserOut, UserIn
from models.structural.TokenModels import Token

router = APIRouter(prefix="/user", tags=["User"], dependencies=[Depends(get_api_key)])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user: UserInDB = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(days=999)
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/register",
    response_model=Dict,
)
async def register_new_user(user: UserIn) -> Dict:
    try:
        user.password = get_password_hash(user.password)
        await create_user(user)
        return {"message": f"User with name {user.name} created successfully!"}
    except Exception as e:
        raise e


@router.get("/", response_model=Optional[List[UserOut]])
async def get_all() -> Optional[List[UserOut]]:
    try:
        users = await get_all_users()
        return users
    except Exception as e:
        raise e