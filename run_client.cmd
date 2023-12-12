cd client
python -m venv .venv
call .venv/scripts/activate
pip install -r requirements.txt
cd src
flask --app client run