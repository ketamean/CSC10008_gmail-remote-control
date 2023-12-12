cd server
python -m venv .venv
call .venv/scripts/activate
pip install -r requirements.txt
cd src
python serverGUI.py