from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, EmailField, SelectField
from wtforms.validators import DataRequired


def AddDepartForm(user_ids):
    class Form(FlaskForm):
        title = StringField('Название департамента', validators=[DataRequired()])
        chief = SelectField('ID начальника', choices=user_ids, validators=[DataRequired()])
        members = StringField('Сотрудники', validators=[DataRequired()])
        email = EmailField('Почта департамента', validators=[DataRequired()])
        submit = SubmitField('Добавить')

    return Form()
