from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, EmailField
from wtforms.validators import DataRequired


class AddDepartForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief = IntegerField('ID начальника', validators=[DataRequired()])
    members = StringField('Сотрудники', validators=[DataRequired()])
    email = EmailField('Почта департамента', validators=[DataRequired()])
    submit = SubmitField('Добавить')
