import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    surname = sa.Column(sa.String)
    name = sa.Column(sa.String)
    age = sa.Column(sa.Integer)
    email = sa.Column(sa.String, unique=True)
    hashed_password = sa.Column(sa.String)
    modified_date = sa.Column(sa.DateTime)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.id} {self.name} {self.email}>"
