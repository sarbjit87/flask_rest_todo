from flask import Flask, request, jsonify, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os

from marshmallow import Schema, fields, validate

# Initialize the App and database
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'secret_key_for_app'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
                                        'sqlite:///' + os.path.join(basedir, 'database1.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        hashed_password = generate_password_hash(password, method='sha256')
        self.password = hashed_password

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_token(self):
        payload = {
                    'public_id' : self.public_id,
                    'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                  }
        return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )

    def __repr__(self):
        return f"User('{self.username}')"

# Define Marshmallow Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('password', 'username')
    username = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=5))

# Initialize Schema
user_schema = UserSchema()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        try:
            if ('access_token' in request.headers['Authorization']):
                req_header_token = request.headers['Authorization']
                token = req_header_token.split()[1]
        except Exception as e:
            print("Error", e)

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/user', methods=['POST'])
def register_user():
    errors = user_schema.validate(request.json)
    if errors:
        abort(422, str(errors))

    username = request.json['username']
    password = request.json['password']
    new_user = User(public_id=str(uuid.uuid4()), username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user created!'}), 201


@app.route('/login', methods=['POST'])
def login():
    authdata = request.authorization
    errors = user_schema.validate(authdata)
    if errors:
        abort(422, str(errors))

    username = authdata['username']
    password = authdata['password']

    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response(jsonify({'Error': 'User not found'}), 401)

    if user.verify_password(password):
        token = user.generate_token()
        return jsonify({'token' : token.decode('UTF-8')})

    return make_response(jsonify({'Error': 'Invalid username/password'}), 401)

@app.route('/home', methods=['GET'])
@token_required
def home():
    return make_response(jsonify({'Message': 'Home Page'}))

if __name__ == '__main__':
    app.run(debug=True)
