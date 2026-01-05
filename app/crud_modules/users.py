from sqlalchemy.orm import Session

from .. import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_profile_image(db: Session, user_id: int, image_url: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.profile_image_url = image_url
        db.commit()
        db.refresh(db_user)
    return db_user


def update_user_profile(db: Session, user_id: int, user_update: schemas.UserBase):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user_update.name is not None:
            db_user.name = user_update.name
        if user_update.email is not None:
            db_user.email = user_update.email
        db.commit()
        db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, hashed_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.hashed_password = hashed_password
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def create_admin_user_if_not_exists(db: Session, admin_email: str, admin_password: str, admin_name: str, get_password_hash_func):
    db_user = get_user_by_email(db, email=admin_email)
    if not db_user:
        hashed_password = get_password_hash_func(admin_password)
        admin_user = models.User(name=admin_name, email=admin_email, hashed_password=hashed_password)
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Usuário administrador '{admin_email}' criado.")
        return admin_user
    print(f"Usuário administrador '{admin_email}' já existe.")
    return db_user