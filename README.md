# dnsripoff
Simple flask App or my try to copy DNS site functionality.

## How to run:
1. Create folder
```bash
mkdir dnsripoff
cd dnsripoff
```
2. Create venv
```bash
python3 -m venv dnsripoff
source dnsripoff/bin/activate
```
3. Install requirements
```bash
pip install flask flask-sqlalchemy flask-login
```
4. Create folder and clone
```bash
mkdir dnsripoff_app
git clone https://github.com/n3z0xx/dnsripoff.git
```
5. Create setting.py with
```python
SECRET_KEY = 'secret-key-goes-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
```
6. Init db(you can use python REPL)
```python
from dnsripoff_app import db, create_app
db.create_all(app=create_app())
```
7. Run
```bash
export FLASK_APP=dnsripoff_app
export FLASK_DEBUG=1
flask run
```
