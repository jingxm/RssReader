from werkzeug.security import generate_password_hash, check_password_hash

pw = '123456'
pw_hash = generate_password_hash(pw)
print pw_hash