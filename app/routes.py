from flask import Flask, flash, redirect, url_for, request, render_template
from passlib.hash import sha256_crypt

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import exc
import secrets

import re
import datetime

from app import app, client, db
from app.models import Character,Move,CharacterLog, Log, User, Confirmation
from app.get_images import get_images
from app.confirmation_email import set_confirmation_code

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def generate_key():
    generated_key = secrets.token_urlsafe(32)
    print(generated_key)
    return generated_key


def hash_password(password):
    return sha256_crypt.encrypt(password)

def checkIncludesExcludes(includeExclude):
    if not includeExclude:
        return includeExclude
    else:
        return includeExclude.split(",")

def passwordChecker(email, password, confirmed_password):

    password_return_object = {"error_messages": []}

    #Verify valid email
    password_return_object["email_error"] = not re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)
    if password_return_object["email_error"]: password_return_object["error_messages"].append("Your email is invalid")
    
    #Verify passwords match
    password_return_object["no_match"] = password != confirmed_password
    if password_return_object["no_match"]: password_return_object["error_messages"].append("The passwords do not match")

    # check if password is too short
    password_return_object["too_short"] = len(password) < 8
    if password_return_object["too_short"]: password_return_object["error_messages"].append("Your password is too short. Minimum length is 8 characters")

    # check if password is too long
    password_return_object["too_long"] = len(password) > 128
    if password_return_object["too_long"]: password_return_object["error_messages"].append("Your password is too long. Maximum length is 128 characters")

    # searching for digits
    password_return_object["digit_error"] = re.search(r"\d", password) is None
    if password_return_object["digit_error"]: password_return_object["error_messages"].append("Your password requires at least one digit")

    # searching for uppercase
    password_return_object["uppercase_error"] = re.search(r"[A-Z]", password) is None
    if password_return_object["uppercase_error"]: password_return_object["error_messages"].append("Your password requires at least one uppercase letter")

    # searching for lowercase
    password_return_object["lowercase_error"] = re.search(r"[a-z]", password) is None
    if password_return_object["lowercase_error"]: password_return_object["error_messages"].append("Your password requires at least one lowercase letter")

    # searching for symbols
    password_return_object["symbol_error"] = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None
    if password_return_object["symbol_error"]: password_return_object["error_messages"].append("Your password requires at least one special character")

    # overall result
    password_return_object["password_ok"] = not (password_return_object["email_error"] or password_return_object["no_match"] or password_return_object["too_short"] or password_return_object["too_long"] or password_return_object["digit_error"] or password_return_object["uppercase_error"] or password_return_object["lowercase_error"] or password_return_object["symbol_error"] )

    return password_return_object

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    error=None
    if request.method == "POST":
        password_result = passwordChecker(request.form["email"], request.form["password"], request.form["confirm_password"])
        if not password_result["password_ok"]:
            for error in password_result["error_messages"]:
                flash(error)
        else:
            userSQL=User(username=request.form["username"], email=request.form["email"],hashed_password=sha256_crypt.encrypt(request.form["password"]), apikey=generate_key(), usertype="user")
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
    return render_template('account.html', user=current_user)

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

@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/api/character/all', methods=["GET"])
def characterData():

    if("include" in request.args and "exclude" in request.args):
        return "Can not use both 'include' and 'exclude' options", 400

    characters = {}
    for character in Character.query.all():
        characters[character.value] = character.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
        characters[character.value]["count"] = CharacterLog.query.filter(CharacterLog.CharacterName==character.value).count()

    writeLog(request)
    return characters

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    dbChar = Character.query.get(character)
    try:
        if request.args.get("extra"):
            data= dbChar.serialize_extra_move_data()
        else:
            data= dbChar.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
    except AttributeError:
        return f'{character} is not a valid character', 404
    if "ERROR_MESSAGE" in data:
        return data["ERROR_MESSAGE"], data["ERROR_CODE"]

    writeLog(request)
    return data

@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):

    try:
        moveData = Move.query.get(move).serialize()
    except AttributeError:
        return f'{move} is not a valid move', 404
        
    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    if request.args.get("images"):
        moveData["imgData"] = get_images(client, move, request)
    writeLog(request)
    return moveData



@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    writeLog(request)
    return obj

def writeLog(request):
    print("here")
    user=User.query.filter(User.apikey==request.headers.get('API-Key')).first()

    if(not user):
        log = Log(ip=request.remote_addr, url=request.url)
    else:
        log = Log(ip=request.remote_addr, url=request.url, username=user.username)
    
    writeToDB([log])

def writeToDB(SQL):
    for statement in SQL:
        db.session.add(statement)
    db.session.commit()