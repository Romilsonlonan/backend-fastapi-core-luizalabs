from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

from ...dependencies import get_current_active_user, get_db
from ... import schemas
from ...core.container import DIContainer
from .service import UserService
from ...config import settings
from ...security import create_access_token

router = APIRouter(tags=["Users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return DIContainer.get_user_service(db)

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, service: UserService = Depends(get_user_service)):
    return service.register_user(user)

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: UserService = Depends(get_user_service),
):
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
):
    return current_user

@router.put("/users/me/", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserBase,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    service: UserService = Depends(get_user_service),
):
    return service.update_profile(current_user.id, user_update)

@router.put("/users/me/password", response_model=schemas.User)
async def change_password(
    password_data: schemas.PasswordChange,
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    service: UserService = Depends(get_user_service),
):
    return service.change_password(current_user.id, password_data)

@router.delete("/users/me/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    service: UserService = Depends(get_user_service),
):
    service.delete_user(current_user.id)

@router.post("/users/me/photo", response_model=schemas.User)
async def upload_profile_image(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
    file: Annotated[UploadFile, File()],
    service: UserService = Depends(get_user_service),
):
    UPLOAD_DIRECTORY = "uploaded_images"
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension.lower() not in [".png", ".jpg", ".jpeg", ".gif"]:
        raise HTTPException(status_code=400, detail="Formato de imagem inválido.")

    file_location = os.path.join(UPLOAD_DIRECTORY, f"{current_user.id}{file_extension}")
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    image_url = f"http://localhost:8000/{UPLOAD_DIRECTORY}/{current_user.id}{file_extension}"
    return service.update_profile_image(current_user.id, image_url)
