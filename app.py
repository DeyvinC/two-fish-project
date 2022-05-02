from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from email.policy import default

from forms import SignInForm, LoginForm

from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
    login_user,
)



#Flask
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "THISISMYSECRETKEY"

#Database
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

db.create_all()

#Authorization
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None

## Tables

class Todo(db.Model):
    __table_name__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_due = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, default=datetime.utcnow)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    todos = db.relationship('Todo', backref='user')

    def set_password(self, password):
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User %r>" % self.id

# Routes

@app.route('/', methods=['POST', 'GET'])
def index():
    if not current_user.is_authenticated:
        return redirect("/login")
    if request.method == "POST":
        task_content = request.form["content"]
        task_date_due = request.form['date_due']
        datetime_object = datetime.fromisoformat(task_date_due)
        new_task = Todo(content=task_content, date_due=datetime_object, user_id=current_user.get_id())

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except: 
            return 'There was an error'

    tasks = Todo.query.order_by(Todo.date_created).filter_by(
        user_id=current_user.id).all()
    logged_in_user = User.query.filter_by(id=current_user.id).first()
    return render_template("index.html", tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)


    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating the task'

    else:
        return render_template('update.html', task=task)

@app.route('/complete/<int:id>', methods=["POST"])
def completeTask(id):
    task_to_complete = Todo.query.get_or_404(id)
    task_to_complete.completed = True

    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to complete task"

@app.route('/incomplete/<int:id>', methods=['POST'])
def uncompleteTask(id):
    task_to_complete = Todo.query.get_or_404(id)
    task_to_complete.completed = False

    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Unable to complete task"


@app.route("/completed")
def completed():
    tasks = Todo.query.order_by(Todo.completed.desc()).filter_by(
        user_id=current_user.id).all()
    logged_in_user = User.query.filter_by(id=current_user.id).first()
    return render_template("index.html", tasks=tasks, user=logged_in_user)

@app.route("/notcompleted")
def notcompleted():
    tasks = Todo.query.order_by(Todo.completed).filter_by(
        user_id=current_user.id).all()
    logged_in_user = User.query.filter_by(id=current_user.id).first()
    return render_template("index.html", tasks=tasks, user=logged_in_user)

@app.route("/datedue")
def date_due():
    tasks = Todo.query.order_by(Todo.date_due).filter_by(
        user_id=current_user.id).all()
    logged_in_user = User.query.filter_by(id=current_user.id).first()
    return render_template("index.html", tasks=tasks, user=logged_in_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            return redirect("/")
        flash("Invalid email or password")
        return redirect("/login")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/signup", methods=["POST", "GET"])
def signUp():
    form = SignInForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user is None:
            user = User(
                firstName=form.firstName.data.capitalize(),
                lastName=form.lastName.data.capitalize(),
                email=form.email.data.lower(),
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect("/")
        flash("A user already exists with this email address")

    return render_template("signup.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)