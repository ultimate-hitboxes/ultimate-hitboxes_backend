from flask import Flask, flash, redirect, url_for, request, render_template
from sqlalchemy import exc
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from app.verification import check_password, generate_key, hash_password
import datetime
from passlib.hash import sha256_crypt

from app import app, client, db
from app.models import User, Confirmation
from app.confirmation_email import set_confirmation_code

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.get_user_by_username_or_email(request.form["username"])
        if not user or not sha256_crypt.verify(request.form["password"], user.hashed_password):
           flash("Invalid Login")
           return render_template('login.html') 
        else:
            login_user(user)
            return redirect(url_for('account'))
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    error=None
    if request.method == "POST":
        password_result = check_password(request.form["email"], request.form["password"], request.form["confirm_password"])
        if not password_result["password_ok"]:
            for error in password_result["error_messages"]:
                flash(error)
        else:
            userSQL=User(username=request.form["username"], email=request.form["email"],hashed_password=sha256_crypt.encrypt(request.form["password"]), apikey=generate_key(), usertype="user")
            print(userSQL.hashed_password)
            try:
                db.session.add(userSQL)
                db.session.commit()
                
            except exc.IntegrityError:
                db.session.rollback()
                flash("This username or email are already in use")
                return render_template('register.html')

            set_confirmation_code(request.form["email"],request.form["username"])
            return redirect(url_for('account'))
    return render_template('register.html', error=error)


@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    if request.method == "GET":
        if(current_user.authenticated):
            return render_template('account.html', user=current_user)
        else:
            return render_template('account_confirmation.html')
    if request.method == "POST":
        codes = Confirmation.query.filter(Confirmation.email==current_user.email).all()
        for code in codes:
            if(code.confirmation_code==request.form["confirmation_code"] and datetime.datetime.utcnow() < code.expires_at):
                current_user.authenticated=True
                db.session.commit()
                return render_template('account.html', user=current_user)
        flash("Invalid Confirmation Code, it may be expired")
        return render_template('account_confirmation.html')

@app.route('/new_confirmationcode', methods=["POST"])
@login_required
def new_confirmationcode():
    set_confirmation_code(current_user.email,current_user.username)
    return redirect(url_for('account'))

@app.route('/new_apikey', methods=["POST"])
@login_required
def new_apikey():
    new_key = generate_key()
    current_user.apikey=new_key
    db.session.commit()
    return redirect(url_for('account'))

@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return render_template('index.html')