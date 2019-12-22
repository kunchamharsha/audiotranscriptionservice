virtualenv -p python2 venv
source venv/bin/activate
python setup.py
python models/models.py
mv mynah.db ../crud/
python app.py