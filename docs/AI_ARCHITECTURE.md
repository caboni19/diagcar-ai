# DZ Nova Architecture

## Goal
The system diagnoses probable vehicle faults from symptoms written in French, Arabic, Darija, or mixed language.

## AI Pipeline
1. User enters symptoms.
2. `nlp_service.py` normalizes text and expands multilingual synonyms.
3. `ai_engine.py` loads diagnostic cases from MySQL.
4. TF-IDF converts textual symptoms into numeric vectors.
5. Logistic Regression predicts possible fault classes.
6. RapidFuzz computes semantic-like similarity between user input and database cases.
7. The system combines ML probability and fuzzy similarity into one probability score.
8. The top ranked faults are returned with OBD code, severity, and recommendation.

## Why this counts as AI
The project uses NLP, machine learning classification, probabilistic scoring, and automated decision support. It is not only a static keyword website.
