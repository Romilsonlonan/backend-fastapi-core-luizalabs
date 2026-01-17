from sqlalchemy.orm import Session

from .. import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        name=user.name or "Usuário", 
        email=user.email.lower(), 
        hashed_password=hashed_password,
        profession=user.profession
    )
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


def update_user_subscription(db: Session, user_id: int, status: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.subscription_status = status
        db.commit()
        db.refresh(db_user)
    return db_user


def create_admin_user_if_not_exists(db: Session, admin_email: str, admin_password: str, admin_name: str, get_password_hash_func):
    email_lower = admin_email.lower()
    db_user = get_user_by_email(db, email=email_lower)
    if not db_user:
        hashed_password = get_password_hash_func(admin_password)
        admin_user = models.User(
            name=admin_name, 
            email=email_lower, 
            hashed_password=hashed_password,
            subscription_status='premium',
            profession='Administrador'
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Usuário administrador '{email_lower}' criado.")
        return admin_user
    print(f"Usuário administrador '{email_lower}' já existe.")
    return db_user
