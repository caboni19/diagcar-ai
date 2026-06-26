DIAGCAR AI - GRADUATION PROJECT VERSION
=======================================

This is a complete rebuild of the website using:
- Flask backend
- XAMPP MySQL database
- Hybrid AI diagnostic engine
- Fuzzy NLP for French / Arabic / Darija symptoms
- Machine Learning classification model using TF-IDF + Logistic Regression
- Fault probability scoring
- Saved users and saved diagnostic history
- Voice symptom input using browser Web Speech API

---------------------------------------
1) INSTALL XAMPP
---------------------------------------
1. Open XAMPP Control Panel.
2. Start Apache and MySQL.
3. Open phpMyAdmin:
   http://localhost/phpmyadmin

---------------------------------------
2) CREATE DATABASE
---------------------------------------
In phpMyAdmin:
1. Click SQL.
2. Copy everything from:
   database/schema.sql
3. Run it.

This creates:
- diagcar_ai database
- users table
- diagnostic_cases table
- diagnostics table

---------------------------------------
3) CREATE PYTHON ENVIRONMENT
---------------------------------------
Open terminal inside the project folder:

Windows PowerShell:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

If python command does not work, try:
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

---------------------------------------
4) CONFIGURE DATABASE
---------------------------------------
Copy:
.env.example

Rename it to:
.env

Default XAMPP MySQL values are already set:
DB_USER=root
DB_PASSWORD=
DB_NAME=diagcar_ai

If your MySQL has a password, put it in DB_PASSWORD.

---------------------------------------
5) IMPORT DIAGNOSTIC DATASET
---------------------------------------
Run:
python scripts/import_cases.py

You should see:
Imported XX diagnostic cases into MySQL.

---------------------------------------
6) RUN WEBSITE
---------------------------------------
Run:
python run.py

Open in browser:
http://127.0.0.1:5000

---------------------------------------
7) HOW TO PROVE AI IS USED
---------------------------------------
This project uses real AI components:

1. Natural Language Processing:
   - Text normalization
   - Accent removal
   - Arabic/French/Darija synonym expansion
   - Multilingual symptom understanding

2. Fuzzy NLP:
   - rapidfuzz token_set_ratio compares user symptoms with diagnostic cases
   - works even if the user writes incomplete or mixed-language input

3. Machine Learning:
   - scikit-learn TF-IDF character n-grams transform text into numerical features
   - Logistic Regression predicts the most likely diagnostic case
   - The API returns ML probability and fuzzy score

4. Hybrid AI scoring:
   - Final probability = ML prediction + fuzzy NLP similarity
   - Results are ranked by probability

5. Voice AI input:
   - Browser speech recognition allows speaking symptoms instead of typing

Important files to show your teacher:
- app/services/ai_engine.py
- app/services/nlp_service.py
- app/routes/api.py
- database/schema.sql

---------------------------------------
8) TEST EXAMPLES
---------------------------------------
Try these symptoms:

French:
Le voyant moteur est allumé et la voiture consomme trop d'essence

Arabic/Darija:
السيارة تسخن بزاف وضو الزيت شاعل

Mixed:
bruit bizarre au démarrage and battery faible

---------------------------------------
9) PROJECT STRUCTURE
---------------------------------------
app/
  routes/       Flask routes and API
  services/     AI and NLP engine
  utils/        Database connection

templates/      HTML pages
static/         CSS and JS
database/       MySQL schema
data/           Diagnostic CSV dataset
scripts/        Import tools
docs/           Documentation

---------------------------------------
10) IMPORTANT NOTE
---------------------------------------
This project does not need an external paid AI API to work.
It uses local AI/ML methods that can be demonstrated directly in code.
