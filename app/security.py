from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from .config import settings


# Usar bcrypt diretamente para evitar problemas do passlib
def verify_password(plain_password, hashed_password):
    print(f"Attempting to verify password for plain_password: {plain_password}")
    print(f"Hashed password from DB: {hashed_password}")
    # Truncar senha para 72 bytes (limite do bcrypt)
    plain_password_encoded = plain_password.encode('utf-8')[:72]
    if isinstance(hashed_password, str):
        hashed_password_encoded = hashed_password.encode('utf-8')
    else:
        hashed_password_encoded = hashed_password
    
    result = bcrypt.checkpw(plain_password_encoded, hashed_password_encoded)
    print(f"Password verification result: {result}")
    return result


def get_password_hash(password):
    # Truncar senha para 72 bytes (limite do bcrypt)
    password = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
