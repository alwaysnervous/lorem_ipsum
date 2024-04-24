from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


def AddApplicationForm():
    text = """Представим ситуацию:
    Есть коллектив, занимающийся разработкой дизайна.\n
    Этому коллективу нужно развитие и грамотный РR, чтобы получать заказы :)\n\n
    Какими будут Ваши первые действия, придя в этот коллектив, будучи менеджером по продуктам?"""

    class Form(FlaskForm):
        allocates_time = StringField('Сколько времени Вы выделите на работу в проекте?', validators=[DataRequired()])
        what_doing = StringField('Чем Вы занимаетесь?', validators=[DataRequired()])
        self_actions = StringField(text, validators=[DataRequired()])
        submit = SubmitField('Отправить')

    return Form()
