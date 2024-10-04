from sqlalchemy.orm import Session
import api.models as models
import api.schemas as schemas


def create_interaction(db: Session, interaction: schemas.InteractionCreate):
    db_interaction = models.Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


def get_interactions_by_contact(
        db: Session,
        contact_id: int,
        skip: int = 0,
        limit: int = 100
        ):
    return db.query(
        models.Interaction
        ).filter(
            models.Interaction.contact_id == contact_id
            ).offset(skip).limit(limit).all()
