from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quilltask.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='todo')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Yahan par 'username' likha gaya hai, taki yeh HTML form ke name attribute se match kare.
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user_by_name = User.query.filter_by(name=username).first()
        if user_by_name:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(name=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
        
    return render_template('layouts/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('layouts/login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        title = request.form.get('title')
        status = request.form.get('status')
        new_todo = Todo(title=title, status=status, user=current_user)
        db.session.add(new_todo)
        db.session.commit()
        flash('Task added!', 'success')
        return redirect(url_for('dashboard'))
    
    todos = current_user.todos
    todo_tasks = [t for t in todos if t.status == 'todo']
    progress_tasks = [t for t in todos if t.status == 'in-progress']
    completed_tasks = [t for t in todos if t.status == 'completed']

    return render_template('index.html', user_name=current_user.name, todo_tasks=todo_tasks, progress_tasks=progress_tasks, completed_tasks=completed_tasks)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    todo_to_edit = Todo.query.get_or_404(todo_id)
    if todo_to_edit.user != current_user:
        flash('You are not authorized to edit this task.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        todo_to_edit.title = request.form.get('title')
        todo_to_edit.status = request.form.get('status')
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    todos = current_user.todos
    todo_tasks = [t for t in todos if t.status == 'todo']
    progress_tasks = [t for t in todos if t.status == 'in-progress']
    completed_tasks = [t for t in todos if t.status == 'completed']
    
    return render_template('index.html', user_name=current_user.name, todo=todo_to_edit, todo_tasks=todo_tasks, progress_tasks=progress_tasks, completed_tasks=completed_tasks)

@app.route('/delete/<int:todo_id>', methods=['POST'])
@login_required
def delete(todo_id):
    todo_to_delete = Todo.query.get_or_404(todo_id)
    if todo_to_delete.user != current_user:
        flash('You are not authorized to delete this task.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(todo_to_delete)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/update_status/<int:todo_id>', methods=['POST'])
@login_required
def update_status(todo_id):
    todo_to_update = Todo.query.get_or_404(todo_id)
    if todo_to_update.user != current_user:
        flash('You are not authorized to update this task.', 'danger')
        return redirect(url_for('dashboard'))
    
    new_status = request.form.get('status')
    todo_to_update.status = new_status
    db.session.commit()
    flash('Task status updated!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
