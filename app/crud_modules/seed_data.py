from sqlalchemy.orm import Session
from .. import models

def seed_appointment_data(db: Session):
    # Seed Services
    if db.query(models.Service).count() == 0:
        services = [
            models.Service(name="Consulta Inicial", duration=60, price=250.0, description="Primeira consulta para avaliação geral."),
            models.Service(name="Retorno", duration=30, price=150.0, description="Consulta de acompanhamento."),
            models.Service(name="Avaliação Nutricional", duration=45, price=200.0, description="Medições e bioimpedância."),
            models.Service(name="Consultoria Esportiva", duration=90, price=400.0, description="Planejamento de alta performance.")
        ]
        db.add_all(services)
    
    # Seed Locations
    if db.query(models.Location).count() == 0:
        locations = [
            models.Location(name="Consultório Principal", address="Av. Paulista, 1000", is_online=False),
            models.Location(name="Centro de Treinamento", address="Rua do Futebol, 500", is_online=False),
            models.Location(name="Atendimento Online", address="Google Meet / Zoom", is_online=True)
        ]
        db.add_all(locations)
    
    db.commit()
