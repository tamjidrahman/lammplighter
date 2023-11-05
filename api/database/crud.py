from uuid import UUID

from sqlalchemy import Column, update
from sqlalchemy.orm import Session

from api.database import models, schemas


def get_input_by_name(db: Session, name: str) -> models.InputConfig | None:
    return db.query(models.InputConfig).filter(models.InputConfig.name == name).first()


def get_inputs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InputConfig).offset(skip).limit(limit).all()


def get_runs(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Run, models.InputConfig)
        .join(models.InputConfig, models.Run.input_id == models.InputConfig.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_run_status(db: Session, run_id: Column[UUID], status: str):
    db.execute(
        update(models.Run)
        .where(models.Run.id == run_id)
        .values({models.Run.status: status})
    )
    db.commit()


def create_inputconfig(db: Session, inputconfig: schemas.InputConfigCreate):
    db_inputconfig = models.InputConfig(
        name=inputconfig.name, s3_path=inputconfig.s3_path
    )
    db.add(db_inputconfig)
    db.commit()
    db.refresh(db_inputconfig)
    return db_inputconfig


def create_run(db: Session, run: schemas.RunCreate) -> models.Run | None:
    inputconfig_name = run.inputconfig_name
    db_inputconfig = get_input_by_name(db, inputconfig_name)
    if db_inputconfig is None:
        return None

    db_run = models.Run(input_id=db_inputconfig.id, commands=run.commands, status="NEW")
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run
