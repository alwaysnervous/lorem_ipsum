import datetime

import sqlalchemy as sa
from data.db_session import SqlAlchemyBase

association_table = sa.Table('association', SqlAlchemyBase.metadata,
                             sa.Column('jobs', sa.Integer, sa.ForeignKey('jobs.id')),
                             sa.Column('category', sa.Integer,
                                       sa.ForeignKey('category.id'))
                             )


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)


class Jobs(SqlAlchemyBase):
    __tablename__ = 'jobs'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    team_leader = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    job = sa.Column(sa.String, nullable=True)
    work_size = sa.Column(sa.Integer, nullable=True)
    collaborators = sa.Column(sa.String, nullable=True)
    start_date = sa.Column(sa.DateTime, default=datetime.datetime.now)
    end_date = sa.Column(sa.DateTime, default=datetime.datetime.now)
    is_finished = sa.Column(sa.Boolean, nullable=True)
    category = sa.Column(sa.Integer, sa.ForeignKey("category.id"))
    thumbnail_file = sa.Column(sa.Integer, nullable=True)

    user = sa.orm.relationship('User')
    categories = sa.orm.relationship("Category",
                                     secondary="association",
                                     backref="jobs")

    def __repr__(self):
        return f"<Jobs {self.id} {self.job} {self.is_finished}>"
