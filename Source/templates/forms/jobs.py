from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, DateTimeField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    job = StringField('Название работы', validators=[DataRequired()])
    team_leader = IntegerField('ID руководителя команды', validators=[DataRequired()])
    collaborators = StringField('Команда', validators=[DataRequired()])
    start_date = DateTimeField('Дата начала (YYYY-MM-DD HH:MM:SS)')
    end_date = DateTimeField('Дата окончания')
    is_finished = BooleanField('Работа закончена?')
    submit = SubmitField('Добавить')
