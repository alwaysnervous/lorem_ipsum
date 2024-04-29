from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, SelectField, FileField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired


def AddJobForm(user_full_names_and_ids, category_names_and_ids):
    class Form(FlaskForm):
        job = StringField('Название работы', validators=[DataRequired()])
        team_leader = SelectField('Руководитель команды', choices=user_full_names_and_ids, validators=[DataRequired()])
        collaborators = SelectMultipleField('Команда', choices=user_full_names_and_ids, validators=[DataRequired()])
        work_size = IntegerField('Время выполнения работы', validators=[DataRequired()])
        category = SelectField('Категория дизайна', choices=category_names_and_ids)
        is_finished = BooleanField('Работа закончена?')
        thumbnail_file = FileField('Файл миниатюры')
        submit = SubmitField('Добавить')

    return Form()
