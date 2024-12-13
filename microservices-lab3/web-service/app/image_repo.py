import json
from typing import Optional
from sqlmodel import Session, select

import db


def save_image(id: str, original_name: str, thumbnails: dict):
    model = db.ImageModel(id=id, original_name=original_name,
                          thumbnails_json=json.dumps(thumbnails))
    with Session(db.engine) as session:
        session.add(model)
        session.commit()


def get_image_by_id(id: str) -> Optional[db.ImageModel]:
    with Session(db.engine) as session:
        return session.get(db.ImageModel, id)


def get_all_images() -> list[db.ImageModel]:
    with Session(db.engine) as session:
        statement = select(db.ImageModel)
        return session.exec(statement).all()
