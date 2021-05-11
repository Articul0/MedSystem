from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user
from UserLogin import UserLogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    work_days = db.Column(db.Integer, nullable=False)
    wage_rate = db.Column(db.Float, default=1)
    score = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Article {self.id}'
        #return '<Article %r>' % self.id


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, Employee)


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/employees')
def employees():
    employees = Employee.query.order_by(Employee.name).all()
    return render_template("employees.html", employees=employees)


@app.route('/employees/<int:id>/edit', methods=['POST', 'GET'])
def employee_edit(id):
    employee = Employee.query.get(id)
    if request.method == "POST":
        employee.name = request.form['name']
        employee.login = request.form['login']
        employee.category = request.form['category']
        employee.work_days = request.form['work_days']
        employee.wage_rate = request.form['wage_rate']
        employee.score = request.form['score']
        employee.source = request.form['source']

        try:
            db.session.add(employee)
            db.session.commit()
            return redirect('/employees')
        except:
            return "Ошибка при редактировании работника"
    else:
        return render_template("employee_edit.html", employee=employee)


@app.route('/employees/<int:id>/delete')
def employee_delete(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        return render_template("employees.html")
    except:
        return 'Ошибка при удалении'


@app.route('/add-employee', methods=['POST', 'GET'])
def add_employee():
    if request.method == "POST":
        name = request.form['name']
        login = request.form['login']
        password = generate_password_hash(request.form['password'])
        category = request.form['category']
        work_days = request.form['work_days']
        wage_rate = request.form['wage_rate']
        score = request.form['score']
        source = request.form['source']

        employee = Employee(name=name, login=login, password=password, category=category, work_days=work_days,
                            wage_rate=wage_rate, score=score, source=source)
        try:
            db.session.add(employee)
            db.session.commit()
            return redirect('/employees')
        except:
            return "Ошибка при добавлении работника"
    else:
        return render_template("add_employee.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        #try:
            login = request.form['login']
            password = generate_password_hash(request.form['password'])
            user = Employee.query.filter_by(login=login)
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect('/')
        #except:
            return "Ошибка при авторизации"
    else:
        return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)

