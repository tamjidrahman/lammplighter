from sqlalchemy.orm import Session

from . import models, schemas


def get_input_by_name(db: Session, name: str):
    return (
        db.query(models.InputConfig)
        .filter(models.InputConfig.name == name)
        .first()
    )


def get_inputs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InputConfig).offset(skip).limit(limit).all()


def get_runs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Run).offset(skip).limit(limit).all()


# def create_input(db: Session, item: schemas.ItemCreate):


def create_inputconfig(db: Session, inputconfig: schemas.InputConfigCreate):
    db_inputconfig = models.InputConfig(
        name=inputconfig.name, s3_path=inputconfig.s3_path
    )
    db.add(db_inputconfig)
    db.commit()
    db.refresh(db_inputconfig)
    return db_inputconfig


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
