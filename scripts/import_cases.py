import csv
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CSV_PATH = ROOT / "data" / "diagcar2026.csv"

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "diagcar_ai"),
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
)
cur = conn.cursor()
cur.execute("DELETE FROM diagnostic_cases")
with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        cur.execute(
            """INSERT INTO diagnostic_cases
            (id_car,categorie,sous_categorie,nom_francais,description_darija,description_arabe,mots_cles_fr,codes_obd,niveau_gravite,action_recommandee,source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE categorie=VALUES(categorie), sous_categorie=VALUES(sous_categorie), nom_francais=VALUES(nom_francais), description_darija=VALUES(description_darija), description_arabe=VALUES(description_arabe), mots_cles_fr=VALUES(mots_cles_fr), codes_obd=VALUES(codes_obd), niveau_gravite=VALUES(niveau_gravite), action_recommandee=VALUES(action_recommandee), source=VALUES(source)""",
            (row.get("id_car"), row.get("categorie"), row.get("sous_categorie"), row.get("nom_francais"), row.get("description_darija"), row.get("description_arabe"), row.get("mots_cles_fr"), row.get("codes_obd"), row.get("niveau_gravite"), row.get("action_recommandee"), row.get("source")),
        )
        count += 1
conn.commit()
cur.close()
conn.close()
print(f"Imported {count} diagnostic cases into MySQL.")
