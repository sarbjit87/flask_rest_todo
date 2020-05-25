from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask import make_response

# Initialize the App and database
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
                                        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define SQLAlchemy Models

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

# Define Marshmallow Schema
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

# Initialize Schema
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found'}), 404)

# Add a new task
@app.route('/task', methods=['POST'])
def add_task():
    print(request)
    name = request.json['name']
    new_task = Task(name)
    db.session.add(new_task)
    db.session.commit()
    return task_schema.jsonify(new_task), 201

# Get All Tasks
@app.route('/task', methods=['GET'])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)

# Get Single Task
@app.route('/task/<id>', methods=['GET'])
def get_task(id):
    task = Task.query.get_or_404(id)
    return task_schema.jsonify(task)

# Update a Task
@app.route('/task/<id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    name = request.json['name']
    task.name = name
    db.session.commit()
    return task_schema.jsonify(task)

# Delete Task
@app.route('/task/<id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return task_schema.jsonify(task)


if __name__ == '__main__':
    app.run(debug=True)
