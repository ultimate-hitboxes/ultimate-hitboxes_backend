from flask import Flask, redirect, url_for, request, render_template, json
from passlib.hash import sha256_crypt

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import secrets

from app import app, client, db
from app.models import Character,Move,CharacterLog, Log, User, Confirmation
from app.get_images import get_images
from app.confirmation_email import send_confirmation_email, generate_confirmation_code

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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print(request.form)
        userSQL=User(username=request.form["username"], email=request.form["email"],hashed_password=sha256_crypt.encrypt(request.form["password"]), apikey=generate_key(), usertype="user")
        
        writeToDB([userSQL])
        confirmation_code=generate_confirmation_code()
        confirmationCodeSQL=Confirmation(email=request.form["email"], confirmation_code=confirmation_code)
        send_confirmation_email(request.form["email"], confirmation_code, request.form["username"])
        writeToDB([confirmationCodeSQL])
        return redirect(url_for('account'))
    else:
        return render_template('register.html')

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
            if(code.confirmation_code==request.form["confirmation_code"]):
                current_user.authenticated=True
                db.session.commit()
                return render_template('account.html', user=current_user)
        return render_template('account_confirmation.html')

@app.route('/new_apikey', methods=["POST"])
@login_required
def new_apikey():
    new_key = generate_key()
    current_user.apikey=new_key
    db.session.commit()
    return render_template('account.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.get_user_by_username_or_email(request.form["username"])
        print(user)
        if sha256_crypt.verify(request.form["password"], user.hashed_password):
            print("Verified")
        else:
            print("Invalid PW")
        login_user(user)
        return redirect(url_for('account'))
    else:
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

    moveObj = Move.query.get(move)
    if not moveObj:
        return f'{move} is not a valid move', 404
    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    writeLog(request)
    return moveObj.serialize()



@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    writeLog(request)
    return obj

def writeLog(request):
    user=User.query.filter(User.apikey==request.headers['API-Key']).first()

    if(not user):
        log = Log(ip=request.remote_addr, url=request.url)
    else:
        log = Log(ip=request.remote_addr, url=request.url, username=user.username)
    
    writeToDB([log])

def writeToDB(SQL):
    for statement in SQL:
        db.session.add(statement)
    db.session.commit()