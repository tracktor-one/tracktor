import re
import secrets

from flask import request, jsonify
from flask_jwt import current_identity

from app import app, authenticated, db, Config
from app.models import User

PASSWORD_SECURITY = re.compile('((?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[_\\-/!@#$%^&*\\\\]).{8,30})')
ADMIN_PASSWORD_RESET = ''


@app.route('/admin/user')
@authenticated()
def list_all_users():
    users = [user.toJSON() for user in User.query.all()]
    return jsonify(users=users)


@app.route('/admin/user/<user_id>')
@authenticated()
def get_single_user(user_id) -> tuple:
    user = User.query.filter_by(public_id=user_id).first()
    return (jsonify(user.toJSON()), 200) if user else (jsonify(error="No user found with ID {}".format(user_id)), 404)


@app.route('/admin/user', methods=['PUT'])
@authenticated(admin=True)
def create_user() -> tuple:
    data = request.get_json()
    name = data.get('name') if data else None
    password = data.get('password') if data else None

    if not name or not password:
        return jsonify(error="Unable to create user"), 400

    if User.query.filter_by(name=name).first():
        return jsonify(error="Name already taken"), 409

    return jsonify(User.create(
        name=name,
        password=password
    ).toJSON()), 200


@app.route('/admin/user/<user_id>', methods=['POST'])
@authenticated(admin=True)
def update_user(user_id) -> tuple:
    data = request.get_json()
    name = data.get('name') if data else None
    admin = data.get('admit') if data else None
    if data is None or not name or not admin:
        return jsonify(error="Unable to update user"), 400

    user = User.query.filter_by(public_id=user_id).first()
    if not user:
        return jsonify(error="No user found with ID {}".format(user_id)), 404

    if user.id == 1 and not admin:
        return jsonify(error="Super admin can not be degraded"), 409

    if not user.is_username_valid(name):
        return jsonify(error="Name already taken"), 409

    user.name = name
    user.admin = admin
    db.session.commit()
    return '', 204


@app.route('/admin/pwreset/master')
def reset_admin_password() -> tuple:
    global ADMIN_PASSWORD_RESET
    token = request.args.get("token")
    if ADMIN_PASSWORD_RESET == "" or not token:
        ADMIN_PASSWORD_RESET = secrets.token_urlsafe(64)
        app.logger.info(f"ADMIN PASSWORD RESET TOKEN: {ADMIN_PASSWORD_RESET}")
        response = {"message": "A new reset token was generated. Check the logs of this server"}
        if app.debug:
            response["token"] = ADMIN_PASSWORD_RESET
        return jsonify(response), 200
    if token != ADMIN_PASSWORD_RESET:
        return jsonify(error="Invalid reset token"), 403
    User.query.get(1).update_password(Config.ADMIN_PASSWORD)
    db.session.commit()
    ADMIN_PASSWORD_RESET = ""
    return jsonify(message=f"Admin password is now set to: {Config.ADMIN_PASSWORD}"), 200


@app.route('/admin/pwreset', methods=['POST'])
@authenticated()
def change_password() -> tuple:
    user = User.query.get(current_identity.id)
    username = request.args.get("user")
    password = request.get_json().get("password") if request.get_json() else None
    if username:
        if user.is_admin():
            user = User.query.filter_by(name=username).first()
            if not user:
                return jsonify(error="No user found with name {}".format(username)), 404
        else:
            return jsonify(error="Insufficant permissions".format(username)), 403
    if not password or not PASSWORD_SECURITY.match(password):
        return jsonify(
            error="The password must have at least 8 characters, including a digit, a lowercase, an uppercase and a special character".format(
                username)), 400
    return ('', 204) if user.update_password(password) else (jsonify(error="Password not updated"), 400)


@app.route('/admin/user/<user_id>', methods=['DELETE'])
@authenticated(admin=True)
def remove_user(user_id) -> tuple:
    if user_id == current_identity.public_id:
        return jsonify(error="User can not be deleted by same user"), 409

    user = User.query.filter_by(public_id=user_id).first()

    if not user:
        return jsonify(error="No user found with ID {}".format(user_id)), 404

    if user.id == 1:
        return jsonify(error="Super admin can not be deleted"), 409

    db.session.delete(user)
    db.session.commit()
    return '', 204
