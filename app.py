from flask import Flask, render_template, request
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'key'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()

    todos= Todo.query.order_by(Todo.id.desc()).all()
    return render_template('index.html', todos= todos)

if __name__ == '__main__':
    app.run(debug=True)