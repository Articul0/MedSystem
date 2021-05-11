from flask import Flask, render_template, url_for, request, redirect
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
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<heads %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return Heads.query.get(int(user_id))


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            email = request.form['email']
            password = request.form['password']
            user = Heads.query.filter_by(email=email).first()
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                return "Неверный пароль"
        except:
            return "Ошибка при авторизации"
    else:
        return render_template("login.html")


@app.route('/')
@app.route('/home')
def index():
    try:
        user = current_user.email
    except:
        user = ''
    return render_template("index.html", user=user)


@app.route('/about')
@login_required
def about():
    logout_user()
    return "Теперь вы не авторизированы"
    #return render_template("about.html")


@app.route('/employees')
@login_required
def employees():
    try:
        user = current_user.email
    except:
        user = ''
    employees = Employees.query.order_by(Employees.name).all()
    return render_template("employees.html", employees=employees, user=user)


@app.route('/employees/<int:id>/edit', methods=['POST', 'GET'])
@login_required
def employee_edit(id):
    try:
        user = current_user.email
    except:
        user = ''
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
        return render_template("employee_edit.html", employee=employee, user=user)


@app.route('/employees/<int:id>/delete')
@login_required
def employee_delete(id):
    employee = Employees.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.flush()
        db.session.commit()
        return render_template("employees.html")
    except:
        db.session.rollback()
        return 'Ошибка при удалении'


@app.route('/add-employee', methods=['POST', 'GET'])
@login_required
def add_employee():
    try:
        user = current_user.email
    except:
        user = ''
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
        return render_template("add_employee.html", user=user)


@app.route('/register', methods=["POST", "GET"])
@login_required
def register():
    try:
        user = current_user.email
    except:
        user = ''
    if request.method == "POST":
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        user = Heads(email=email, password=password, role=role)
        try:
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            return redirect('/')
        except:
            db.session.rollback()
            return "Ошибка при регистрации"
    else:
        return render_template("register.html", user=user)


@app.route('/data', methods=["POST", "GET"])
@login_required
def data():
    try:
        user = current_user.email
    except:
        user = ''
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
        return render_template("employees.html", employees=employees, user=user)
    else:
        return render_template("data.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)

