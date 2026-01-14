from sqlalchemy.orm import Session
from .. import crud_modules as crud
from ..crud_modules.seed_data import seed_appointment_data
from ..config import settings
from ..security import get_password_hash
from ..dependencies import get_db

def initialize_data():
    """
    Inicializa dados básicos do sistema (Admin e Seeds).
    """
    db_gen = get_db()
    db = next(db_gen)
    try:
        crud.create_admin_user_if_not_exists(
            db,
            settings.ADMIN_EMAIL,
            settings.ADMIN_PASSWORD,
            settings.ADMIN_NAME,
            get_password_hash,
        )
        seed_appointment_data(db)
    finally:
        db.close()
