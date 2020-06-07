import requests
import datetime

SERVER = "127.0.0.1:5000"

# Get All Tasks

response = requests.get('http://127.0.0.1:5000/task')

if response.status_code == 200:
    print(response.json())


# Get Individual Task

# Valid Task
response = requests.get('http://127.0.0.1:5000/task/2')

if response.status_code == 200:
    print(response.json())

# Invalid Task
response = requests.get('http://127.0.0.1:5000/task/999')

if not response.status_code == 200:
    print(response.json())


# Add new task

date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
task_string = "This is a task added on %s"%(date)

response = requests.post('http://127.0.0.1:5000/task', json={'name' : task_string})

if response.status_code == 201:
    print(response.json())


# Update an existing task

task_string = "This is a task which is updated"

response = requests.put('http://127.0.0.1:5000/task/3', json={'name' : task_string})

if response.status_code == 200:
    print(response.json())


# Delete an existing task

response = requests.delete('http://127.0.0.1:5000/task/3')

if response.status_code == 200:
    print(response.json())
