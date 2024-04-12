import sqlalchemy
from .db_session import SqlAlchemyBase


class InfoList(SqlAlchemyBase):
    __tablename__ = "infolist"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    countries = sqlalchemy.Column(sqlalchemy.String, nullable=True)
