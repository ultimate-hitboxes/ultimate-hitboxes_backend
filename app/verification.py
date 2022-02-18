from passlib.hash import sha256_crypt
import secrets
import re

def generate_key():
    generated_key = secrets.token_urlsafe(32)
    return generated_key

def hash_password(password):
    return sha256_crypt.encrypt(password)

def check_password(email, password, confirmed_password):

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