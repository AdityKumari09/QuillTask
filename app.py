from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'key'
db = SQLAlchemy(app)

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='todo')

# Create database tables (if not exists)
with app.app_context():
    db.create_all()

# Home Route - Add / Update Tasks
@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:todo_id>', methods=['GET', 'POST'])
def index(todo_id=None):
    if request.method == 'POST':
        title = request.form.get('title')
        status = request.form.get('status') or 'todo'

        if todo_id is None:
            # Add new task
            todo = Todo(title=title, status=status)
            db.session.add(todo)
            db.session.commit()
            flash('Todo item added successfully', 'success')
        else:
            # Update existing task
            todo = Todo.query.get(todo_id)
            if todo:
                todo.title = title
                todo.status = status
                db.session.commit()
                flash('Todo item updated successfully', 'success')

        return redirect(url_for('index'))

    # If editing a task, fetch it
    todo = None
    if todo_id is not None:
        todo = Todo.query.get(todo_id)

    # Fetch all tasks
    todos = Todo.query.order_by(Todo.id.desc()).all()

    # Group tasks by status
    todo_tasks = [t for t in todos if t.status == 'todo']
    progress_tasks = [t for t in todos if t.status == 'in-progress']  # ✅ fixed from 'progress'
    completed_tasks = [t for t in todos if t.status == 'completed']

    return render_template(
        'index.html',
        todos=todos,
        todo=todo,
        todo_tasks=todo_tasks,
        progress_tasks=progress_tasks,
        completed_tasks=completed_tasks
    )

# Delete Task
@app.route('/todo-delete/<int:todo_id>', methods=["POST"])
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash('Todo item deleted successfully', 'success')
    return redirect(url_for('index'))

# Update status (used for checkbox marking complete)
@app.route('/update_status/<int:todo_id>', methods=['POST'])
def update_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_status = request.form.get('status')
    if new_status in ['todo', 'in-progress', 'completed']:
        todo.status = new_status
        db.session.commit()
        flash('Task status updated!', 'success')
    return redirect(url_for('index'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
