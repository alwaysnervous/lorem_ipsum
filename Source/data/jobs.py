import datetime

import sqlalchemy as sa
from data.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)


class Jobs(SqlAlchemyBase):
    __tablename__ = 'jobs'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    job = sa.Column(sa.String, nullable=True)
    team_leader = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    collaborators = sa.Column(sa.String, nullable=True)
    work_size = sa.Column(sa.Integer, nullable=True)
    category = sa.Column(sa.Integer, sa.ForeignKey("category.id"))
    is_finished = sa.Column(sa.Boolean, nullable=True)
    thumbnail_file = sa.Column(sa.Integer, nullable=True)
