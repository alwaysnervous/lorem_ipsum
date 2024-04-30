import logging

from flask import Flask, render_template, redirect, flash, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.applications import Application
from data.jobs import Jobs, Category
from data.users import User
from forms.applications import AddApplicationForm
from forms.jobs import AddJobForm
from forms.users import RegisterForm, LoginForm

from ip_api import get_city_by_ip

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
login_manager = LoginManager(app)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

ALLOWED_PHOTO_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp',
                            'ico', 'svg', 'tif', 'bmp']


def calculate_time_difference_in_hours(date1, date2):
    time_difference = date2 - date1
    total_seconds = time_difference.total_seconds()
    hours = total_seconds / 3600
    return hours


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.get(User, user_id)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = User(
            email=form.login.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        if not session.query(User).all():
            user.is_admin = True
        session.add(user)
        session.commit()
        session.close()
        return redirect("/")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash("Неправильный логин или пароль", "danger")
        return render_template("login.html", form=form)
    return render_template("login.html", title="Авторизация", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add-job", methods=["GET", "POST"])
@login_required
def add_job():
    session = db_session.create_session()
    user_full_names_and_ids = {user.id: f"{user.name} {user.surname}" for user in session.query(User).all()}
    category_names_and_ids = {category.id: category.name for category in session.query(Category).all()}
    form = AddJobForm(tuple(f"{user_id}. {user_full_name}" for user_id, user_full_name
                            in user_full_names_and_ids.items()),
                      tuple(f"{category_id}. {category_name}" for category_id, category_name
                            in category_names_and_ids.items()))
    if form.validate_on_submit():
        filename = None
        if 'thumbnail_file' in request.files:
            f = request.files['thumbnail_file']
            filename = f.filename.replace(' ', '-')
            if filename != '':
                if filename.split('.')[-1] not in ALLOWED_PHOTO_EXTENSIONS:
                    flash("Некорректное имя файла!", 'error')
                    session.close()
                    return redirect("/")
                with open(f'Source/static/img/cases/{filename}', 'wb') as file:
                    file.write(f.read())
                    logging.info(f"Изображение сохранено в Source/static/img/{filename}")
        job = Jobs(
            job=form.job.data,
            team_leader=form.team_leader.data.split(".")[0],
            collaborators=",".join(collaborator.split(".")[0] for collaborator in form.collaborators.data),
            work_size=form.work_size.data,
            category=form.category.data.split(".")[0],
            is_finished=form.is_finished.data,
            thumbnail_file=filename
        )
        session.add(job)
        session.commit()
        session.close()
        return redirect('/')
    if current_user.is_admin:
        session.close()
        return render_template("add_job.html", form=form, title="Добавление работы")
    session.close()
    return redirect('/')


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    session = db_session.create_session()
    user_full_names_and_ids = {user.id: f"{user.name} {user.surname}" for user in session.query(User).all()}
    category_names_and_ids = {category.id: category.name for category in session.query(Category).all()}
    form = AddJobForm(tuple(f"{user_id}. {user_full_name}" for user_id, user_full_name
                            in user_full_names_and_ids.items()),
                      tuple(f"{category_id}. {category_name}" for category_id, category_name
                            in category_names_and_ids.items()))
    filename = None
    if request.method == "GET":
        job = session.query(Jobs).filter(Jobs.id == job_id,
                                         (Jobs.team_leader == current_user.id) | (
                                                 current_user.id == 1)).first()
        if job:
            form.job.data = job.job
            form.team_leader.data = f"{job.team_leader}. {user_full_names_and_ids[job.team_leader]}"
            form.collaborators.data = tuple(f"{int(collaborator_id)}. {user_full_names_and_ids[int(collaborator_id)]}"
                                            for collaborator_id in job.collaborators.split(","))
            form.work_size.data = job.work_size
            form.category.data = category_names_and_ids[job.category]
            form.is_finished.data = job.is_finished
            if job.thumbnail_file:
                filename = job.thumbnail_file
        else:
            session.close()
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id,
                                         (Jobs.team_leader == current_user.id) | (
                                                 current_user.id == 1)).first()
        if job:
            if 'thumbnail_file' in request.files:
                f = request.files['thumbnail_file']
                filename = f.filename.replace(' ', '-')
                if filename != '':
                    if filename.split('.')[-1] not in ALLOWED_PHOTO_EXTENSIONS:
                        flash("Некорректное имя файла!", 'error')
                        session.close()
                        return redirect("/")
                    with open(f'Source/static/img/cases/{filename}', 'wb') as file:
                        file.write(f.read())
                        logging.info(f"Изображение сохранено в Source/static/img/cases/{filename}")
                        job.thumbnail_file = filename
            job.job = form.job.data
            job.team_leader = form.team_leader.data.split(".")[0]
            job.collaborators = ",".join(collaborator.split(".")[0] for collaborator in form.collaborators.data)
            job.work_size = form.work_size.data
            job.category = form.category.data.split(".")[0]
            job.is_finished = form.is_finished.data
            session.commit()
            session.close()
            return redirect('/')
        else:
            session.close()
            abort(404)
    session.close()
    return render_template('add_job.html', thumbnail_file=filename, form=form, title='Редактирование работы')


@app.route("/delete-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def delete_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id,
                                     (Jobs.team_leader == current_user.id) | current_user.is_admin).first()

    if job:
        session.delete(job)
        session.commit()
        session.close()
    else:
        session.close()
        abort(404)
    return redirect('/')


@app.route("/")
def portfolio():
    city = get_city_by_ip(request.headers.get('True-Client-Ip'))
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    categories = session.query(Category).all()
    applications = session.query(Application).all()
    names = {name.id: (name.surname, name.name) for name in users}
    category_names = {category.id: category.name for category in categories}
    collaborators_names = {job.id: ",\n".join([" ".join(names[int(collaborator_id)])
                                               for collaborator_id in job.collaborators.split(',')]) for job in jobs}
    restricted_to_application = set(application.user_id for application in applications)
    session.close()
    return render_template("index.html", jobs=jobs,
                           names=names,
                           category_names=category_names,
                           collaborators_names=collaborators_names,
                           restricted_to_application=restricted_to_application,
                           city=city,
                           title='Журнал работ')


@app.route("/applications")
def application_list():
    session = db_session.create_session()
    applications = session.query(Application).all()
    users = session.query(User).all()
    full_names = {user.id: f"{user.surname} {user.name}" for user in users}
    emails = {user.id: user.email for user in users}
    session.close()
    if current_user.is_admin:
        return render_template("applications.html",
                               applications=applications,
                               full_names=full_names,
                               emails=emails,
                               title='Список заявок')
    return redirect('/')


@app.route('/add-application', methods=['GET', 'POST'])
def add_application():
    session = db_session.create_session()
    applications = session.query(Application).all()
    restricted_to_application = set(application.user_id for application in applications)
    form = AddApplicationForm()
    if form.validate_on_submit():
        depart = Application(
            user_id=current_user.id,
            allocates_time=form.allocates_time.data,
            what_doing=form.what_doing.data,
            self_actions=form.self_actions.data
        )
        session.add(depart)
        session.commit()
        session.close()
        return redirect('/applications')
    if current_user.id not in restricted_to_application:
        session.close()
        return render_template('add_application.html', title='Подача заявки', form=form)
    session.close()
    return redirect('/')


@app.route('/edit-application', methods=['GET', 'POST'])
@login_required
def edit_uncertain_application():
    session = db_session.create_session()
    applications = session.query(Application).all()
    restricted_to_application = set(application.user_id for application in applications)
    if current_user.id in restricted_to_application:
        application_id = session.query(Application.id).filter(Application.user_id == current_user.id).first()[0]
        session.close()
        return redirect(f'/edit-application/{application_id}')
    session.close()
    return redirect('/add-application')


@app.route('/edit-application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    form = AddApplicationForm()
    if request.method == "GET":
        session = db_session.create_session()
        application = session.query(Application).filter(Application.id == application_id,
                                                        (current_user.id == Application.user_id)
                                                        | current_user.is_admin).first()
        if application:
            form.allocates_time.data = application.allocates_time
            form.what_doing.data = application.what_doing
            form.self_actions.data = application.self_actions
        else:
            session.close()
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        application = session.query(Application).filter(Application.id == application_id,
                                                        (current_user.id == Application.user_id)
                                                        | current_user.is_admin).first()
        if application:
            application.allocates_time = form.allocates_time.data
            application.what_doing = form.what_doing.data
            application.self_actions = form.self_actions.data
            session.commit()
            session.close()
            return redirect('/applications')
        else:
            session.close()
            abort(404)
    return render_template('add_application.html', title='Редактирование заявки', form=form)


@app.route("/delete-application/<int:application_id>", methods=["GET", "POST"])
@login_required
def delete_application(application_id):
    session = db_session.create_session()
    application = session.query(Application).filter(Application.id == application_id, current_user.is_admin).first()

    if application:
        session.delete(application)
        session.commit()
        session.close()
    else:
        session.close()
        abort(404)
    return redirect('/applications')


def add_categories(session):
    categories = [(1, 'Графический'),
                  (2, 'Моушен'),
                  (3, 'Веб')]

    for category_id, category_name in categories:
        existing_category = session.query(Category).filter_by(id=category_id).first()
        if not existing_category:
            new_category = Category(id=category_id, name=category_name)
            session.add(new_category)

    session.commit()


def main():
    db_session.global_init("Source/db/base.db")
    session = db_session.create_session()
    add_categories(session)
    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
    main()
