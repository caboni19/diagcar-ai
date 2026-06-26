@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate
echo Installing requirements...
pip install -r requirements.txt
echo Done. Now create the database in phpMyAdmin using database\schema.sql, then run:
echo python scripts\import_cases.py
echo python run.py
pause
