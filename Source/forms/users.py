from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, BooleanField
from wtforms.validators import DataRequired, EqualTo, NumberRange
from wtforms.validators import ValidationError

from data import db_session
from data.users import User


def validate_login(field):
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.email == field.data).first():
        raise ValidationError("Такой пользователь уже существует")


class RegisterForm(FlaskForm):
    login = EmailField("Логин / email", validators=[DataRequired()])

    password = PasswordField("Пароль", validators=[DataRequired()])
    repeat_password = PasswordField("Повтор пароля",
                                    validators=[EqualTo("password", "Пароли должны совпадать")])
    surname = StringField("Фамилия")
    name = StringField("Имя")
    age = IntegerField("Возраст", validators=[NumberRange(1, 99, "Недопустимое целочисленное значение. "
                                                                 "Число должно быть от 1 до 99.")])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
