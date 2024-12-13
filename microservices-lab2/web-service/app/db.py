import json
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel


class ImageModel(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    original_name: str
    thumbnails_json: str

    def get_thumbnails(self) -> dict:
        return json.loads(self.thumbnails_json)


engine = create_engine(
    "postgresql+psycopg2://postgres:password@db/postgres",
    echo=True
)

SQLModel.metadata.create_all(engine)
