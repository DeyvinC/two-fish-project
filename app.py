from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

db.create_all()

class Todo(db.Model):
    __table_name__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # incompleted = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except: 
            return 'There was an error'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        # incomplete = Todo.query.filter_by(complete=False).all()
        complete = Todo.query.filter_by(completed=True).all
        return render_template('index.html', tasks=tasks, complete=complete)

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

@app.route('/complete/<int:id>', methods=['POST'])
def completeTask(id):
    complete_task = Todo.query.get_or_404(id)
    complete_task.completed = True 

    try:
        db.session.commit()
        return redirect('/')
    except:
        'Unable to mark your task as complete'

@app.route('/uncomplete/<int:id>', methods=['POST'])
def uncompleteTask(id):
    uncomplete_task = Todo.query.get_or_404(id)
    uncomplete_task.completed = False

    try:
        db.session.commit()
        return redirect('/')
    except:
        'Unable to mark your task as uncomplete'

if __name__ == '__main__':
    app.run(debug=True)