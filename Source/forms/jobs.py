from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, DateTimeField, SelectField, FileField
from wtforms.validators import DataRequired


def AddJobForm(user_ids, category_ids):
    class Form(FlaskForm):
        job = StringField('Название работы', validators=[DataRequired()])
        team_leader = SelectField('ID руководителя команды', choices=user_ids, validators=[DataRequired()])
        collaborators = StringField('Команда', validators=[DataRequired()])
        start_date = DateTimeField('Дата начала (YYYY-MM-DD HH:MM:SS)')
        end_date = DateTimeField('Дата окончания')
        is_finished = BooleanField('Работа закончена?')
        category = SelectField('ID категории опасности', choices=category_ids)
        thumbnail_file = FileField('Привет')
        submit = SubmitField('Добавить')

    return Form()

