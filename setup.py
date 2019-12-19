import os 

array=[
'flask',
'flask-admin',
'flask-login',
'enum',
'requests',
'python-dateutil',
'sqlalchemy',
'python-dotenv'
]

for package in array:
	os.system('pip install '+package)
