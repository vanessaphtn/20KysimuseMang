from flask import Flask, request, session, jsonify
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'salajane_võti'  # Sessiooni jaoks vajalik

# Laeme CSV sisse rakenduse käivitamisel
df = pd.read_csv("game_data_animals_final.csv")

# 20 küsimust
questions = [
    "Kas see on elus?", "Kas see on loom?", "Kas see on koduloom?", "Kas see on metsloom?",
    "Kas see on suur?", "Kas see on väiksem kui kass?", "Kas sellel on tiivad?", "Kas see ujub?",
    "Kas see elab vees?", "Kas see on imetaja?", "Kas see on lind?", "Kas see on putukas?",
    "Kas see on roheline?", "Kas see kasvab mullas?", "Kas see on söödav?", "Kas see on magus?",
    "Kas see on mineraal?", "Kas see on metall?", "Kas see on haruldane?", "Kas seda kasutatakse ehituses?"
]

words = {
    "animals": ["Kass", "Koer", "Elevant", "Rebane", "Karu"],
    "plants": ["Tulp", "Maasikas", "Porgand", "Tamm", "Kartul"],
    "minerals": ["Raud", "Kuld", "Magneesium", "Kvarts", "Graniit"]
}


@app.route('/')
def index():
    return "Welcome to the game!"

    
@app.route('/api/start', methods=['POST'])
def start_game():
    session["questions"] = df.to_dict(orient="records")  # Salvestame sessiooni
    session["step"] = 0
    return jsonify({"message": "Mäng alustatud!"})
#def start_game():
#    session["step"] = 0  # Alusta uuesti
#    session["category"] = request.json.get("category")  # Kasutaja saab valida kategooria
#    return jsonify({"message": "Mäng alustatud!", "category": session["category"]})

@app.route('/api/question', methods=['GET'])
def get_question():
    step = session.get("step", 0)

    if step >= 19:  # Kui 20 küsimust on küsitud, pakub sõna
        return suggest_word()

    question = questions[step]
    session["step"] += 1  # Liigume järgmise küsimuse juurde
    return jsonify({"question": question})

@app.route('/api/answer', methods=['POST'])
def receive_answer():
    step = session.get("step", 0)
    
    if step >= 20:  # Kui kõik küsimused on küsitud, pakub sõna
        return suggest_word()

    answer = request.json.get("answer", "").lower()
    if answer not in ["jah", "ei", "ei tea"]:
        return jsonify({"message": "Palun vasta 'jah', 'ei' või 'ei tea'!"})
    
    return get_question()  # Liigub järgmise küsimuse juurde

def suggest_word():
    category = session.get("category")
    if category not in words:
        category = random.choice(list(words.keys()))

    suggested_word = random.choice(words[category])
    return jsonify({"message": "Kas sinu sõna oli", "word": suggested_word, "gameOver": True})


# Üldine endpoint, mis tagastab kategooria sõnad
@app.route('/api/words/<category>', methods=['GET'])
def get_words(category):
    if category in words:
        return jsonify(words[category])
    return jsonify({"error": "Sellist kategooriat ei eksisteeri!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
