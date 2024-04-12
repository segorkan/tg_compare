import sqlalchemy
from .db_session import SqlAlchemyBase


class CompareList(SqlAlchemyBase):
    __tablename__ = "comparelist"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    countries = sqlalchemy.Column(sqlalchemy.String, nullable=True)
