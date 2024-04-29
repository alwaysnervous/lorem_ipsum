import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Application(SqlAlchemyBase):
    __tablename__ = 'applications'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), unique=True)
    allocates_time = sa.Column(sa.String)
    what_doing = sa.Column(sa.String)
    self_actions = sa.Column(sa.String)
