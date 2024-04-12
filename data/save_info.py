import sqlalchemy
from .db_session import SqlAlchemyBase


class SaveInfo(SqlAlchemyBase):
    __tablename__ = "saveinfo"

    country = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    intinfo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
