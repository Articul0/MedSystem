from flask import Flask, render_template, url_for, request, redirect, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv
#from UserLogin import UserLogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

login_manager = LoginManager(app)


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    work_days = db.Column(db.Integer, nullable=False)
    wage_rate = db.Column(db.Float, default=1)
    score = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<employees %r>' % self.id


class Heads(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<heads %r>' % self.id


class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, unique=True, nullable=False)
    employee_id = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return '<keys %r>' % self.id


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), unique=True, nullable=False)
    city_coefficient = db.Column(db.Float, unique=True, nullable=False)

    def __repr__(self):
        return '<cities %r>' % self.id


class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<departments %r>' % self.id


class WorkingHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(100), unique=True, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    disability = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<working_hours %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return Heads.query.get(int(user_id))


@app.route('/login', methods=["POST", "GET"])
def login():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    if request.method == "POST":
        try:
            login = request.form['login']
            password = request.form['password']
            user1 = Heads.query.filter_by(login=login).first()
            if check_password_hash(user1.password, password):
                login_user(user1)
                res = make_response(redirect('/'))
                res.set_cookie('authorized', 'true', 60*60)
                return res
            else:
                flash('Неверный пароль', category='error')
                return render_template("login.html", user=user, user_role=user_role)
        except:
            return "Ошибка при авторизации"
    else:
        return render_template("login.html", user=user, user_role=user_role)


@app.route('/')
@app.route('/home')
def index():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    return render_template("index.html", user=user, user_role=user_role)


@app.route('/personal_account')
@login_required
def personal_account():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    if Heads.query.filter_by(login=user).first().role == 'admin':
        return render_template("personal_account_admin.html", user=user, user_role=user_role)
    elif Heads.query.filter_by(login=user).first().role == 'leader':
        return render_template("personal_account_leader.html", user=user, user_role=user_role)
    elif Heads.query.filter_by(login=user).first().role == 'co-worker':
        return render_template("personal_account_coworker.html", user=user, user_role=user_role)


@app.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    if request.method == "POST":
        return "Теперь вы не авторизированы"
    return "Теперь вы не авторизированы"


@app.route('/employees')
@login_required
def employees():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    employees = Employees.query.order_by(Employees.name).all()
    return render_template("employees.html", employees=employees, user=user, user_role=user_role)


@app.route('/employees/<int:id>/edit', methods=['POST', 'GET'])
@login_required
def employee_edit(id):
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    employee = Employees.query.get(id)
    if request.method == "POST":
        employee.name = request.form['name']
        employee.category = request.form['category']
        employee.work_days = request.form['work_days']
        employee.wage_rate = request.form['wage_rate']
        employee.score = request.form['score']
        employee.source = request.form['source']

        try:
            db.session.add(employee)
            db.session.flush()
            db.session.commit()
            return redirect('/employees')
        except:
            db.session.rollback()
            return "Ошибка при редактировании работника"
    else:
        return render_template("employee_edit.html", employee=employee, user=user, user_role=user_role)


@app.route('/employees/<int:id>/delete')
@login_required
def employee_delete(id):
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    employee = Employees.query.get_or_404(id)
    #if request.method == "POST":
    try:
        db.session.delete(employee)
        db.session.flush()
        db.session.commit()
        employees = Employees.query.order_by(Employees.name).all()
        return render_template("employees.html", employees=employees, user=user, user_role=user_role)
    except:
        db.session.rollback()
        return 'Ошибка при удалении'
    #else:
        #return render_template("employee_delete.html", employee=employee, user=user)


@app.route('/add-employee', methods=['POST', 'GET'])
@login_required
def add_employee():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    if request.method == "POST":
        name = request.form['name']
        category = request.form['category']
        work_days = request.form['work_days']
        wage_rate = request.form['wage_rate']
        score = request.form['score']
        source = request.form['source']

        employee = Employees(name=name, category=category, work_days=work_days, wage_rate=wage_rate, score=score,
                             source=source)
        try:
            db.session.add(employee)
            db.session.flush()
            db.session.commit()
            return redirect('/employees')
        except:
            db.session.rollback()
            return "Ошибка при добавлении работника"
    else:
        return render_template("add_employee.html", user=user, user_role=user_role)


@app.route('/register', methods=["POST", "GET"])
def register():
    if not request.cookies.get('authorized'):
        logout_user()
    if request.method == "POST":
        allow_registration = True
        if Heads.query.filter_by(login=request.form['login']).first():
            allow_registration = False
            flash('Пользователь с таким логином уже существует', category='error')
        if Heads.query.filter_by(email=request.form['email']).first():
            allow_registration = False
            flash('Пользователь с такой почтой уже существует', category='error')
        if request.form['password'] != request.form['password_check']:
            allow_registration = False
            flash('Пароли не совпадают', category='error')

        if allow_registration:
            login = request.form['login']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            if request.form['role'] == 'Сотрудник планового отдела':
                role = 'co-worker'
            elif request.form['role'] == 'Руководитель отделения':
                role = 'leader'
            elif request.form['role'] == 'Администратор':
                role = 'admin'
            user = Heads(login=login, email=email, password=password, role=role)
            try:
                db.session.add(user)
                db.session.flush()
                db.session.commit()
                return redirect('/login')
            except:
                db.session.rollback()
                return "Ошибка при регистрации"
        else:
            return render_template("register.html")
    else:
        return render_template("register.html")


@app.route('/load_employees', methods=["POST", "GET"])
@login_required
def load_employees():
    try:
        user = current_user.login
        user_role = Heads.query.filter_by(login=user).first().role
    except:
        user = 'гость'
        user_role = None
    if not request.cookies.get('authorized'):
        logout_user()
    if request.method == "POST":
        f = request.form['csvfile']
        Employees.query.delete()
        with open(f, encoding='utf8', newline='') as file:
            csvfile = csv.reader(file)
            headers = next(csvfile)
            for row in csvfile:
                name = row[0]
                category = row[1]
                work_days = row[2]
                wage_rate = row[3]
                score = row[4]
                source = row[5]

                employee = Employees(name=name, category=category, work_days=work_days, wage_rate=wage_rate,
                                     score=score, source=source)
                try:
                    db.session.add(employee)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    return "Ошибка при добавлении работника"
        employees = Employees.query.order_by(Employees.name).all()
        return render_template("employees.html", employees=employees, user=user, user_role=user_role)
    else:
        return render_template("load_employees.html", user=user, user_role=user_role)


if __name__ == "__main__":
    app.run(debug=True)

