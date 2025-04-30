from flask import Flask, request, jsonify, session
import pandas as pd
from sklearn.neighbors import  NearestNeighbors
import random
from flask_cors import CORS
import uuid
import json

app = Flask(__name__) #, static_folder = "frontend/dist/static", template_folder = "frontend/dist")
app.secret_key = 'super-salajane-võti'
app.config['TIMEOUT'] = 30
CORS(app)


#@app.route('/')
#def index():
#    return render_template("index.html")


# Kategooriad ja failide nimekiri
files = {
    #"animals": "/home/kysimustemang/mysite/game_data_animals_final.csv",
    #"plants": "/home/kysimustemang/mysite/game_data_vegetables_final.csv",
    #"minerals": "/home/kysimustemang/mysite/game_data_minerals_final.csv",
    #"easy": "/home/kysimustemang/mysite/game_data_easy_final.csv"

    "animals": "game_data_animals_final.csv",
    "plants": "game_data_vegetables_final.csv",
    "minerals": "game_data_minerals_final.csv",
    "easy": "game_data_easy_final.csv"
}

files_hyponyms = {
    #"animals": "/home/kysimustemang/mysite/word_hyponyms_animals.txt",
    #"plants": "/home/kysimustemang/mysite/word_hyponyms_vegetables.txt",
    #"minerals": "/home/kysimustemang/mysite/game_data_minerals_final.csv",
    #"easy": "/home/kysimustemang/mysite/game_data_easy_final.csv"
    "animals": "word_hyponyms_animals.txt",
    "plants": "word_hyponyms_vegetables.txt",
    "minerals": "nothing.txt",
    "easy": "nothing.txt"

}

# JSON-failide lugemise ja kirjutamise funktsioonid
def load_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Mängu andmed
games = {}

# Üldine endpoint, mis tagastab kategooria sõnad
@app.route('/api/words/<category>', methods=['GET'])
def get_words(category):
    if category in files:
        game_id = str(uuid.uuid4())
        df = pd.read_csv(files[category])
        words_list = df['Sõna'].tolist()
        games = load_json('games.json')

        games[game_id] = {
        "category": category,
        "possible_words": [],
        "selected_word": "",
        "question_history": [],
        "answer_history": [],
        "answer_history_modified": [],
        "no-count": 0,
        "popular_words": [],
        "guessed_words": [],
        "unique_question_count": 0
        }
        
        save_json(games, 'games.json')
        session['game_id'] = game_id
        return jsonify({"words": words_list, "game_id": game_id})
    return jsonify({"error": "Sellist kategooriat ei eksisteeri!"}), 404

# Algatamine - stardifunktsioon
@app.route('/api/start', methods=['GET'])
def start_game():
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]
    # 1. alustame mängu algoritmi
    return jsonify({"message": "Mäng algatatud"})

@app.route('/api/question', methods=['GET'])
def ask_question():
    #Andmete laadimine 
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]

    #df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history"], game_data)[0]
    #game_data["no-count"] = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history"], game_data)[1]
    df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history_modified"], game_data)[0]
    game_data["no-count"] = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history_modified"], game_data)[1]


    # 2. kontrollitakse, kas võib veel küsimust küsida (step < 20)
    print("HETKEL ON MÄNGU",len(game_data["question_history"]) ,". KÜSIMUS!")
    #print("Mängu andmed:", game_data)
    if len(game_data["question_history"]) <= 19 and game_data["selected_word"] == "":
        question = best_question(df, game_data) 

        if question == "Midagi läks valesti. Küsimused on otsas.":
            return jsonify({"error": question}), 400

        game_data["question_history"].append(question)  
        save_json(games, 'games.json') # Andmete salvestamine
        return jsonify({"question": question})

    # 20 küsimusena pakume sõna
    elif len(game_data["question_history"]) >= 19:
        best_word = game_data["selected_word"]
        game_data["guessed_words"].append(best_word)
        save_json(games, 'games.json')
        return jsonify({"message": "Pakun sõna!", "word": best_word})

    # 6. kui oleme leidnud sobiva sõna, siis pakume seda 
    else:

        best_word = game_data["selected_word"]
        unique_q = unique_question(df, best_word, game_data)
        #print("Arvan, et sõna on:", best_word, " kontrollin seda küsimusega:", unique_q)
        if unique_q and unique_q not in game_data["question_history"] and game_data["unique_question_count"] <=1 and len(game_data["question_history"]) < 19:
            game_data["question_history"].append(unique_q) 
            game_data["unique_question_count"] += 1
            save_json(games, 'games.json') # Andmete salvestamine
            return jsonify({"question": unique_q})
        else:
            if unique_q == False or unique_q in game_data["question_history"] or game_data["unique_question_count"] >=1:
                game_data["guessed_words"].append(best_word)
                save_json(games, 'games.json')
                return jsonify({"message": "Pakun sõna!", "word": best_word})

            # Kui sõna on juba pakutud ja rohkem küsimusi ei tohi küsida
            if best_word in game_data["guessed_words"]:
                save_json(games, 'games.json')
                return jsonify({"message": "Sõna on juba pakutud ja rohkem küsimusi ei küsita."}), 200

            # Kui varem küsitud küsimustele oli "ei" ja püüame olukorda parandada
            if len(game_data["answer_history"]) >= 2:
                #df = get_dataframe(game_data["category"], game_data["question_history"][:-2], game_data["answer_history"][:-2], game_data)[0]
                #game_data["no-count"] = get_dataframe(game_data["category"], game_data["question_history"], game_data["answer_history"], game_data)[1]
                df = get_dataframe(game_data["category"], game_data["question_history"][:-2], game_data["answer_history_modified"][:-2], game_data)[0]
                game_data["no-count"] = get_dataframe(game_data["category"], game_data["question_history"], game_data["answer_history_modified"], game_data)[1]

            question = best_question(df, game_data)

            # Kaitse - kui küsimus on juba küsitud või tühikäik
            if question in game_data["question_history"] or question == "Midagi läks valesti. Küsimused on otsas.":
                save_json(games, 'games.json')
                return jsonify({"message": "Küsimused on otsas või juba küsitud. Pakun sõna!", "word": best_word})

            game_data["question_history"].append(question)  
            save_json(games, 'games.json')
            return jsonify({"question": question})

def get_dataframe(category, questions, answers, game_data):
    df = pd.read_csv(files[category])
    df = df.drop(columns=["Synonyms"], errors='ignore')
    noCount = 0
    if questions == [] and answers == []:
        return df, noCount
    for question, answer in zip(questions, answers):
        filtered = filter_df(df, question, answer, game_data, noCount)
        df = filtered[0]
        print("get dataframe", df.shape, question)
        noCount = filtered[1]
    
    print("get dataframe no-count", noCount)
    return df, noCount

def best_question(df, game_data):
    history = game_data["question_history"]
    if game_data["no-count"] < 6:
        if df is None or df.empty or df.shape[0] == 0 or df.shape[1] == 0:
            print("best question, df tühi võtame algse df-i pealt küsimuse")
            df = get_dataframe(game_data["category"],[],[], game_data)[0]
            remaining_columns = [col for col in df if col not in history and col != "Sõna" and col != "tähtsus" and col != "Synonyms"]
        else:
            remaining_columns = [col for col in df.columns if col not in history and col != "Sõna" and col != "tähtsus" and col != "Synonyms"]

        if not remaining_columns:
            return "Midagi läks valesti. Küsimused on otsas."

    # kui on rohkem kui kolmele viimasele küsimusele eitavalt vastatud, siis eeldame, et kasutaja on millelegi valesti vastanud
    else:
        print("Rohkem kui 5 küsimusele on valesti vastatud!")
        #remaining_columns = back_tracking(history, game_data["answer_history"], game_data)[0]
        #df = back_tracking(history, game_data["answer_history"], game_data)[1]
        remaining_columns = back_tracking(history, game_data["answer_history_modified"], game_data)[0]
        df = back_tracking(history, game_data["answer_history_modified"], game_data)[1]

    if (len(remaining_columns) >= 400 and game_data["category"] == "animals") or (len(remaining_columns) <= 300 and game_data["category"] != "animals"):
        column_scores = []

        for col in remaining_columns:
            yes_count = df[col].value_counts().get(1, 0)  # Mitu korda vastati "jah"
            no_count = df[col].value_counts().get(0, 0)   # Mitu korda vastati "ei"

            # Kui populaarsetest sõnadest paljud vastaksid jaatavalt, suurenda selle veeru väärtust
            popular_yes_count = pd.to_numeric(df[df["tähtsus"] == 1][col], errors='coerce').sum()  # Populaarsete sõnade "jah" vastuste arv

            # Optimaalne küsimus jagab dataset'i pooleks ja eelistab küsimusi, kus tähtsad sõnad vastavad "jah"
            balance_score = abs(yes_count - no_count)  # Mida väiksem, seda paremini jagab dataset'i pooleks
            if game_data["category"] == "easy":
                weighted_score = balance_score - (0.5 * popular_yes_count) + random.uniform(-5, 5)
            else:
                weighted_score = balance_score - (0.5 * popular_yes_count) + random.uniform(-1, 1)

            column_scores.append((col, weighted_score))
        
        print(column_scores)
        # Leia madalaima skooriga (optimaalseim) küsimus
        best_question = min(column_scores, key=lambda x: x[1])[0]
    else:
        best_question = max(remaining_columns, key=lambda col: (df[col].value_counts().get(1, 0)))
    return best_question

def filter_df(df, question, answer, game_data, noCount):
    if len(df["Sõna"].tolist()) == 0 or len(df.columns) <= 2: # andmestik tühi
        #print("backtrackin filter df sees")
        #filtered_df = back_tracking(game_data["question_history"], game_data["answer_history"], game_data)[1]
        #filtered_df = back_tracking(game_data["question_history"], game_data["answer_history_modified"], game_data)[1]
        filtered_df = get_dataframe(game_data["category"],[],[], game_data)[0]
    # 5.1.1 vastus JAH: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele jaatavalt (1)
    if answer == "jah" or answer == 1:
        noCount = 0
        if question in df.columns:
            filtered_df = df[df[question] == 1] # df nüüd ainult sobivad sõnad ja küsimused millel on vähemalt üks väärtus 1
        else:
            return df, noCount
    # 5.2.1 vastus EI: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele eitavalt (0)
    elif answer == "ei" or answer == 0:
        noCount += 1
        if question in df.columns:
            filtered_df = df[df[question] == 0]
        else:
            return df, noCount
    elif answer == 3 or (game_data["category"] == "minerals" and answer == 4) or (game_data["category"] == "easy" and answer == 4): # pakutud sõna polnud õige 
        noCount += 1
        df = pd.read_csv(files[game_data["category"]])
        return df, noCount
    elif answer == 4 and game_data["category"] != "minerals" and game_data["category"] != "easy":  # pakutud sõna oli peaaegu õige
        data = []
        file = files_hyponyms[game_data["category"]]
        with open(file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = eval(line.strip())
                        data.append(entry)
                    except Exception as e:
                        print("Viga real:", line, e)
        guessed_word = question.replace("Kas sõna oli ", "").replace("?", "").strip()
        noCount = 0
        word_hyponyms = []
        df = pd.read_csv(files[game_data["category"]])

        # leiame sõna hüponüümid 
        for words, hyponyms in data:
            if guessed_word in words:
                word_hyponyms = list(hyponyms)
                break
        word_hyponyms.append(guessed_word)

        print("huponyymid", word_hyponyms)
          # Filtreerime ainult need read, mis on seotud sõnadega, millel vähemalt üks jaatav küsimus
        matched_df = df[df["Sõna"].isin(word_hyponyms)]  # Filtreerime vastavalt hüponüümidele
        filtered_df = matched_df.copy()  # Loome koopia, et vältida originaali muutmist

        # Leiame kõik küsimused, millele need hüponüümid jaatavalt vastavad
        yes_columns = [col for col in matched_df.columns if col not in ['Sõna', 'tähtsus', 'Synonyms']]

        # Filtreerime read, kus vähemalt üks küsimus on jaatavalt vastatud
        match_mask = matched_df[yes_columns].applymap(lambda x: str(x).strip() == "1").any(axis=1)

        # Uued andmed, kus vähemalt üks küsimus on jaatav
        filtered_df = matched_df[match_mask]

        print("Filtreeritud DataFrame:")
        print(filtered_df)

    # 5.3.1 vastus EI TEA: arvestame / ei arvesta küsimust küsimute hulk (ei tea kumb on parem valik)
    else:
        return df, noCount

    keep_columns = ["Sõna", "tähtsus"]
    numeric_columns = [col for col in filtered_df.columns if col not in keep_columns]
    filtered_df = filtered_df.loc[:, keep_columns + [col for col in numeric_columns if (filtered_df[col] != 0).any()]]

    final_columns = list(set(keep_columns) | set(filtered_df.columns[(filtered_df != 0).any(axis=0)]))
    return filtered_df.loc[:, final_columns], noCount
    
def words_probability(df, user_answers, game_data, n_neighbors=5, top_n=20):
    filtered_questions = []
    print(game_data["answer_history"],game_data["answer_history_modified"] )
    print(game_data["question_history"])
    for i in range(len(user_answers)):
        #if game_data["answer_history"][i] not in [2,3,4]: # ainult 0 või 1; 
        if game_data["answer_history_modified"][i] not in [2,3,4]: # ainult 0 või 1; 
            filtered_questions.append(game_data["question_history"][i])
    print(filtered_questions)

    question_columns = [col for col in filtered_questions if col in df.columns]
    features = df[question_columns]
    word_labels = df["Sõna"]
    importance_scores = df["tähtsus"]

    if features is None and len(features) == 0:
        print("Invalid features:", features)
        return [], []

    num_samples = features.shape[0]
    adjusted_n_neighbors = min(n_neighbors, num_samples)

    knn = NearestNeighbors(n_neighbors=adjusted_n_neighbors)
    knn.fit(features)

    user_answers = [answer for answer in user_answers if answer not in [2, 3, 4]]

    user_answers_df = pd.DataFrame([user_answers], columns=features.columns)

    distances, indices = knn.kneighbors(user_answers_df)

    closest_words = word_labels.iloc[indices[0][:top_n]].values
    closest_distances = distances[0][:top_n]

    probabilities = 1 / (1 + closest_distances)

    # Lisame tähtsuse mõju
    closest_importance = importance_scores.iloc[indices[0][:top_n]].values
    weighted_probabilities = probabilities * ( 1 / closest_importance)
    return closest_words, weighted_probabilities

def selected_word(df,words_prob, game_data):
    words, probabilities = words_prob

    # kui ainult 1 sõna on jäänud pakume seda
    if len(df["Sõna"].tolist()) == 1:
        if df["Sõna"].tolist()[0] in words_prob[0]:
            if df["Sõna"].tolist()[0] not in game_data["guessed_words"]:
                print("ainult 1 sõna järel")
                return df["Sõna"].tolist()[0]

    # kui alles on ainult 1 levinud sõna, siis pakume seda
    if len(game_data["popular_words"]) == 1:
        if game_data["popular_words"][0] not in game_data["guessed_words"]:
            print("ainult 1 populaarne sõna järel")
            return game_data["popular_words"][0]

    # kui 19 küsimust on küsitud küsime knn-iga kõige lähemat
    if len(game_data["question_history"]) >= 19:
        best_index = probabilities.argmax()
        print("leiame kõige sobivama sõna", words[best_index])
        return words[best_index]

    return ""

def unique_question(df, word, game_data):
    word_row = df[df["Sõna"] == word]
    if word_row.empty:
        return False

    # Leia veerud, kus antud sõna vastus on jah
    excluded_columns = ["Sõna", "tähtsus"]
    relevant_columns = [col for col in df.columns if col not in excluded_columns]
    possible_questions = word_row[relevant_columns].loc[:, word_row[relevant_columns].eq(1).any()].columns

    # Kontrolli, kas teised sõnad vastavad neile veergudele ei
    for question in possible_questions:
        if df[df["Sõna"] != word][question].sum() == 0:
            if question not in game_data["question_history"]:
                return question
    return False

def back_tracking(history, answers, game_data): # leiame viimase jah vastuse ja jätkame sealt edasi
    print("back_tracking")
    if 1 not in answers:
        last_yes_index = 0
    else:
        last_yes_index = len(answers) - 1 - answers[::-1].index(1)
    last_random_index = 0
    if 2 in answers:
        last_yes_index = len(answers) - 1 - answers[::-1].index(2)
    if last_yes_index >= last_random_index:
        index = last_yes_index
    else:
        index = last_random_index
    #for i in range(last_yes_index, last_yes_index +1):
    game_data["answer_history_modified"][index] = 2
    if index + 1 < len(game_data["answer_history_modified"]):
        game_data["answer_history_modified"][index + 1] = 2 # muudame kõik kahtlased vastused "ei teaks", et suurendada andmestikku
         # muudame kõik kahtlased vastused "ei teaks", et suurendada andmestikku
    print("backtrack", game_data["answer_history"],game_data["answer_history_modified"] )
    #df = get_dataframe(game_data["category"],game_data["question_history"][:last_yes_index],game_data["answer_history"][:last_yes_index], game_data)[0]
    df = get_dataframe(game_data["category"],game_data["question_history"][:index],game_data["answer_history_modified"][:index], game_data)[0]

    last_question = game_data["question_history"][index]
    print("backtracking 1", df.shape)
    filtered_df = filter_df(df, last_question, 2, game_data, game_data["no-count"])[0]

    if filtered_df is None or filtered_df.empty:
        df = get_dataframe(game_data["category"],[],[], game_data)
        remaining_columns = [col for col in df if col not in history and col != "Sõna" and col != "tähtsus" and col != "Synonyms"]
    else:
        remaining_columns = [col for col in filtered_df.columns if col not in history and col != "Sõna" and col != "tähtsus" and col != "Synonyms"]
    game_data["no-count"] = 0
    print("backtracking", df.shape)
    return remaining_columns, df

@app.route('/api/answer', methods=['POST'])
def answer():
    #Andmete laadimine 
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]
    #df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history"], game_data)
    df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history_modified"], game_data)

    # 4. mängija vastab JAH, EI, EI TEA
    user_answer = request.json.get("answer")
    if user_answer == "jah":
        game_data["answer_history"].append(1)
        game_data["answer_history_modified"].append(1)
    elif user_answer == "ei":
        game_data["answer_history"].append(0)
        game_data["answer_history_modified"].append(0)
    else:
        game_data["answer_history"].append(2)
        game_data["answer_history_modified"].append(2)

    question = game_data["question_history"][-1]
   #df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history"], game_data)[0]
    #game_data["no-count"] = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history"], game_data)[1]
    df = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history_modified"], game_data)[0]
    game_data["no-count"] = get_dataframe(game_data["category"],game_data["question_history"],game_data["answer_history_modified"], game_data)[1]

    print("Vastati küsimusele: '",question, "' vastusega:", user_answer, ".Peale, mida andmestik on: ", df.shape)

    # Salvestame tõenäolised sõnad 
    game_data["popular_words"] = df.loc[df["tähtsus"] == 1, "Sõna"].tolist()
    print("popular words:", game_data["popular_words"])
    df_algne = get_dataframe(game_data["category"],[],[], game_data)[0]
    #words_probabilities = words_probability(df_algne, game_data["answer_history"], game_data)
    words_probabilities = words_probability(df_algne, game_data["answer_history_modified"], game_data)
    game_data["possible_words"] = words_probabilities[0].tolist()
    print("possible words:", game_data["possible_words"])
    game_data["selected_word"] = selected_word(df, words_probabilities, game_data)
    #print(game_data["selected_word"])

    #print("enne salvestamist andmed: ", game_data)

    save_json(games, 'games.json')

    return ask_question()

@app.route('/api/history', methods=['GET'])
def show_history():
    #Andmete laadimine 
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]

    if len (game_data["question_history"]) >= 18:
         return jsonify({
        "questions": game_data["question_history"],
        "answers": game_data["answer_history"]
         })

    return jsonify({
        "questions": game_data["question_history"][:-1],
        "answers": game_data["answer_history"]
    })

@app.route('/api/undo', methods=['POST'])
def undo_last_question():
    #Andmete laadimine 
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]

    if len(game_data["answer_history"]) > 0:
        # Kui viimane vastus on 0, uuendame no-count väärtust
        if game_data["answer_history"][-1] == 0:
            game_data["no-count"] = max(0, game_data["no-count"] - 1)

        # Eemaldame viimase küsimuse ja vastuse ja andmestiku
        game_data["answer_history"].pop()
        game_data["answer_history_modified"].pop()
        game_data["question_history"].pop()

        save_json(games, 'games.json')

        return jsonify({"message": "Viimane küsimus tühistatud", "question": game_data["question_history"][-1]})
    else:
        return jsonify({"message": "Ei ole enam küsimusi, mida tagastada"}), 400

@app.route('/api/end', methods=['POST'])
def game_end():
    #Andmete laadimine 
    games = load_json("games.json")
    game_id = session.get('game_id')
    if not game_id or game_id not in games:
        return jsonify({"error": "Vale või puuduva game_id"}), 400
    game_data = games[game_id]
    
    print("PAKKUSIN SÕNA, OOTAN LÕPPVASTUST")
    user_answer = request.json.get("answer")

    word = game_data["selected_word"]
    if user_answer == "jah":
        game_data["answer_history"].append(1)
        game_data["answer_history_modified"].append(1)
        game_data["question_history"].append(f"Kas sõna oli {word}?")
        ending = "Ma võitsin!"
        return jsonify({"outcome": ending})
    elif (user_answer == "ei" or  user_answer == "peaaegu") and len(game_data["question_history"]) >= 19:
        game_data["answer_history"].append(0)
        game_data["answer_history_modified"].append(0)
        game_data["question_history"].append(f"Kas sõna oli {word}?")
        ending = "Sa võitsid!"
        return jsonify({"outcome": ending})
    elif user_answer == "ei" or user_answer == "peaaegu":
        if user_answer == "ei":
            game_data["answer_history"].append(3)
            game_data["answer_history_modified"].append(3)

        else:
            game_data["answer_history"].append(4)
            game_data["answer_history_modified"].append(4)
        game_data["question_history"].append(f"Kas sõna oli {word}?")
        game_data["selected_word"] = ""

    save_json(games, 'games.json')
    return jsonify({"continue": True})



if __name__ == '__main__':
    app.run(debug=True)  