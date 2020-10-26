import requests

response = requests.post('http://127.0.0.1:5000/user', json={'username' : "user1", "password" : "Password1!"})

response = requests.post('http://127.0.0.1:5000/login', auth=("user1", "Password1!"))
token = response.json()['token']
head = {'Authorization': 'access_token {}'.format(token)}


#response = requests.get('http://127.0.0.1:5000/home')

r = requests.get('http://127.0.0.1:5000/home', headers=head)
