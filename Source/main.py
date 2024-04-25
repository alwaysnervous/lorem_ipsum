from flask import Flask, render_template, redirect, flash, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.applications import Application
from data.jobs import Jobs, Category
from data.users import User
from forms.applications import AddApplicationForm
from forms.users import RegisterForm, LoginForm
from forms.jobs import AddJobForm

app = Flask(__name__)
login_manager = LoginManager(app)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"


def calculate_time_difference_in_hours(date1, date2):
    time_difference = date2 - date1
    total_seconds = time_difference.total_seconds()
    hours = total_seconds / 3600
    return hours


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User(
            email=form.login.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
    db_sess = db_session.create_session()
    user_ids = [user_id[0] for user_id in db_sess.query(User.id).all()]
    category_ids = [category_id[0] for category_id in db_sess.query(Category.id).all()]
    form = AddJobForm(user_ids, category_ids)
    if form.validate_on_submit():
        job = Jobs(
            job=form.job.data,
            work_size=calculate_time_difference_in_hours(form.start_date.data,
                                                         form.end_date.data),
            team_leader=form.team_leader.data,
            collaborators=form.collaborators.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            category=form.category.data,
            is_finished=form.is_finished.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect("/")
    return render_template("add_job.html", form=form, title="Добавление работы")


@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    db_sess = db_session.create_session()
    user_ids = [user_id[0] for user_id in db_sess.query(User.id).all()]
    category_ids = [category_id[0] for category_id in db_sess.query(Category.id).all()]
    form = AddJobForm(user_ids, category_ids)
    if request.method == "GET":
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id,
                                          (Jobs.team_leader == current_user.id) | (
                                                  current_user.id == 1)).first()
        if jobs:
            form.job.data = jobs.job
            form.team_leader.data = jobs.team_leader
            form.collaborators.data = jobs.collaborators
            form.start_date.data = jobs.start_date
            form.end_date.data = jobs.end_date
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == job_id,
                                          (Jobs.team_leader == current_user.id) | (
                                                  current_user.id == 1)).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader.data
            jobs.collaborators = form.collaborators.data
            jobs.start_date = form.start_date.data
            jobs.end_date = form.end_date.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Job Edit', form=form)


@app.route("/delete-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == job_id,
                                      (Jobs.team_leader == current_user.id) | (current_user.id == 1)).first()

    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/")
def work_log():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    users = db_sess.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", jobs=jobs, names=names, title='Журнал работ')


@app.route("/applications")
def application_list():
    session = db_session.create_session()
    departments = session.query(Application).all()
    users = session.query(User).all()
    names = {name.id: (name.surname, name.name) for name in users}
    if current_user.id == 1:
        return render_template("applications.html", applications=departments, names=names, title='Список заявок')
    else:
        abort(404)


@app.route('/add-application', methods=['GET', 'POST'])
def add_application():
    db_sess = db_session.create_session()
    form = AddApplicationForm()
    if form.validate_on_submit():
        depart = Application(
            allocates_time=form.allocates_time.data,
            what_doing=form.what_doing.data,
            self_actions=form.self_actions.data
        )
        db_sess.add(depart)
        db_sess.commit()
        return redirect('/applications')
    return render_template('add_application.html', title='Подача заявки', form=form)


@app.route('/edit-application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    form = AddApplicationForm()
    if request.method == "GET":
        session = db_session.create_session()
        application = session.query(Application).filter(Application.id == application_id,
                                                        (current_user.id == 1)).first()
        if application:
            form.allocates_time.data = application.allocates_time
            form.what_doing.data = application.what_doing
            form.self_actions.data = application.self_actions
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        application = session.query(Application).filter(Application.id == application_id,
                                                        (current_user.id == 1)).first()
        if application:
            application.allocates_time = form.allocates_time.data
            application.what_doing = form.what_doing.data
            application.self_actions = form.self_actions.data
            session.commit()
            return redirect('/applications')
        else:
            abort(404)
    return render_template('add_application.html', title='Department Edit', form=form)


@app.route('/delete_depart/<int:depart_id>', methods=['GET', 'POST'])
@login_required
def delete_depart(depart_id):
    session = db_session.create_session()
    depart = session.query(Application).filter(Application.id == depart_id,
                                               (Application.chief == current_user.id) | (
                                                       current_user.id == 1)).first()
    if depart:
        session.delete(depart)
        session.commit()
    else:
        abort(404)
    return redirect('/applications')


def add_admins(session):
    categories = [(1, 'low'), (2, 'medium'), (3, 'high')]

    for category_id, category_name in categories:
        existing_category = session.query(Category).filter_by(id=category_id).first()
        if not existing_category:
            new_category = Category(id=category_id, name=category_name)
            session.add(new_category)

    session.commit()


def main():
    db_session.global_init("db/base.db")
    session = db_session.create_session()
    add_admins(session)
    app.run("", port=8080)


if __name__ == '__main__':
    main()
