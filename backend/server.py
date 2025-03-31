from flask import Flask, request, session, jsonify
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
import numpy as np
import random

app = Flask(__name__)
app.secret_key = 'salajane_võti'  # Sessiooni jaoks vajalik

# Kategooriad ja failide nimekiri
files = {
    "animals": "game_data_animals_final.csv",
    "plants": "game_data_vegetables_final.csv",
    "minerals": "game_data_minerals_final.csv"
}

# Mängu andmed 
game_data = {
    "possible_words": [], 
    "selected_word": "",
    "question_history": [],
    "answer_history": [],
    "category": "", 
    "dataset" : None, 
    "current_question": None,
    "selected_word_prop": 0,
    "no-count": 0,
    "dataset_history": [],
    "popular_words": [],
    "guessed_words": [],
    "unique_question_count": 0
}

# Üldine endpoint, mis tagastab kategooria sõnad
@app.route('/api/words/<category>', methods=['GET'])
def get_words(category):
    if category in files:
        df = pd.read_csv(files[category])  
        words_list = df['Sõna'].tolist()
        game_data["possible_words"] = words_list
        game_data["category"] = category 
        game_data["dataset"] = df 
        return jsonify(words_list)
    return jsonify({"error": "Sellist kategooriat ei eksisteeri!"}), 404


# Algatamine - stardifunktsioon
@app.route('/api/start', methods=['GET'])
def start_game():
    if game_data["dataset"] is None:
        return jsonify({"error": "Palun vali esmalt kategooria!"}), 400

    game_data["dataset"] = game_data["dataset"].drop(columns=["Synonyms"], errors='ignore')
    game_data["answer_history"] = []
    game_data["question_history"] = []
    game_data["selected_words"] = None
    game_data["current_question"] = None
    game_data["selected_word_prop"] = 0
    game_data["no-count"] = 0
    game_data["dataset_history"] = [game_data["dataset"]]
    game_data["selected_word"] = ""
    game_data["popular_words"] = []
    game_data["guessed_words"] = []
    game_data["unique_question_count"] = 0
    
    # 1. alustame mängu algoritmi
    return ask_question()


@app.route('/api/question', methods=['GET'])
def ask_question():
    # 2. kontrollitakse, kas võib veel küsimust küsida (step < 20)
    df = game_data["dataset"]
    print("HETKEL ON MÄNGU",len(game_data["question_history"]) ,". KÜSIMUS!")
    print("Mängu ajalugu:", game_data["question_history"])
    if len(game_data["question_history"]) < 19 and game_data["selected_word"] == "":
        question = best_question(df) # 3. küsimuse, mis jagab vastused võimalikult võrdslt pooleks

        if question == "Midagi läks valesti. Küsimused on otsas.":
            return jsonify({"error": question}), 400

        game_data["current_question"] = question  # Salvestame küsimuse
        return jsonify({"question": question})

    # kui sõna valik jäänud 1ni siis küsime sõna

    # 6. kui 20 küsimust saab küsitud kuvame sõna, mille tõenäosus on kõige suurem 
    else:
        best_word = game_data["selected_word"]
        unique_q = unique_question(best_word)
        #print("Arvan, et sõna on:", best_word, " kontrollin seda küsimusega:", unique_q)
        if unique_q and unique_q not in game_data["question_history"] and game_data["unique_question_count"] <=1 and len(game_data["question_history"]) < 19:
            game_data["current_question"] = unique_q
            game_data["unique_question_count"] += 1
            return jsonify({"question": unique_q})
        else:
            if best_word not in game_data["guessed_words"]:
                game_data["guessed_words"].append(best_word)
                #print("Pakun sõna!", best_word)
                game_data["unique_question_count"] = 0
                return jsonify({"message": "Pakun sõna!", "word": best_word})
            elif game_data["question_history"] >= 19:
                return jsonify({"message": "Pakun sõna!", "word": best_word})
            else:
                #print("Sõna on juba pakutud. Küsin uue küsimuse")
                if len(game_data["dataset_history"]) >=2:
                    df = game_data["dataset_history"][-2]
                    game_data["dataset"] = df
    question = best_question(df)
    game_data["current_question"] = question
    #print("uus küsimus on:", question, "df-il:", game_data["dataset"].shape)
    return jsonify({"question": question})

def best_question(df):
    print("best_question df on", df.shape)
    history = game_data["question_history"]
    if game_data["no-count"] < 3: 
        if df is None or df.empty:
            print("best question, df oli tühi võtame essa")
            remaining_columns = [col for col in game_data["dataset_history"][0] if col not in history and col != "Sõna" and col != "tähtsus"]
            df = game_data["dataset_history"][0]
            game_data["dataset"] = df
        else:
            print("best question, df polnud tühi")
            remaining_columns = [col for col in df.columns if col not in history and col != "Sõna" and col != "tähtsus"]

        if not remaining_columns:
            return "Midagi läks valesti. Küsimused on otsas."
    
    # kui on rohkem kui kolmele viimasele küsimusele eitavalt vastatud, siis eeldame, et kasutaja on millelegi valesti vastanud
    else:
        print("Rohkem kui 3 küsimusele on valesti vastatud!")
        remaining_columns = back_tracking(history, game_data["answer_history"])[0]
        df = back_tracking(history, game_data["answer_history"])[1]

    if len(remaining_columns) < 500:
        column_scores = []
        
        for col in remaining_columns:
            yes_count = df[col].value_counts().get(1, 0)  # Mitu korda vastati "jah"
            no_count = df[col].value_counts().get(0, 0)   # Mitu korda vastati "ei"

            # Kui populaarsetest sõnadest paljud vastaksid jaatavalt, suurenda selle veeru väärtust
            popular_yes_count = pd.to_numeric(df[df["tähtsus"] == 1][col], errors='coerce').sum()
            print("popular_yes_count:", popular_yes_count)

            # Optimaalne küsimus jagab dataset'i pooleks ja eelistab küsimusi, kus tähtsad sõnad vastavad "jah"
            balance_score = abs(yes_count - no_count)  # Mida väiksem, seda paremini jagab dataset'i pooleks
            weighted_score = balance_score - (0.5 * popular_yes_count) + random.uniform(-0.5, 0.5)  

            column_scores.append((col, weighted_score))

        # Leia madalaima skooriga (optimaalseim) küsimus
        best_question = min(column_scores, key=lambda x: x[1])[0]
    else:
        best_question = max(remaining_columns, key=lambda col: (df[col].value_counts().get(1, 0)))

    return best_question

def filter_df(df, question, answer):
    print("filter_df selle df, küsimus ja vastus", df.shape, question, answer)
    if len(df["Sõna"].tolist()) == 0 or len(df.columns) <= 2:
        print("backtrackin filter df sees")
        filtered_df = back_tracking(game_data["question_history"], game_data["answer_history"])[1]
    # 5.1.1 vastus JAH: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele jaatavalt (1)
    if answer == "jah":
        game_data["no-count"] = 0
        filtered_df = df[df[question] == 1] # df nüüd ainult sobivad sõnad ja küsimused millel on vähemalt üks väärtus 1
    # 5.2.1 vastus EI: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele eitavalt (0)
    elif answer == "ei":
        game_data["no-count"] += 1
        filtered_df = df[df[question] == 0]
    # 5.3.1 vastus EI TEA: arvestame / ei arvesta küsimust küsimute hulk (ei tea kumb on parem valik) 
    else:
        return df 

    keep_columns = ["Sõna", "tähtsus"]
    numeric_columns = [col for col in filtered_df.columns if col not in keep_columns]
    filtered_df = filtered_df.loc[:, keep_columns + [col for col in numeric_columns if (filtered_df[col] != 0).any()]]
    
    final_columns = list(set(keep_columns) | set(filtered_df.columns[(filtered_df != 0).any(axis=0)]))
    return filtered_df.loc[:, final_columns]

def words_probability(df, user_answers, n_neighbors=5, top_n=20):
    filtered_questions = []
    for i in range(len(game_data["answer_history"])):
        if game_data["answer_history"][i] not in [2,3,4]: # ainult 0 või 1; 2 jäetakse välja
            filtered_questions.append(game_data["question_history"][i])

    question_columns = [col for col in filtered_questions if col in df.columns]  
    features = df[question_columns]
    word_labels = df["Sõna"]  
    importance_scores = df["tähtsus"]  

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

def selected_word(df,words_prob):
    words, probabilities = words_prob

    # kui ainult 1 sõna on jäänud pakume seda 
    if len(df["Sõna"].tolist()) == 1:
        if df["Sõna"].tolist()[0] in words_prob[0]:
            if df["Sõna"].tolist()[0] not in game_data["guessed_words"]:
                return df["Sõna"].tolist()[0]

    # kui alles on ainult 1 levinud sõna, siis pakume seda 
    if len(game_data["popular_words"]) == 1:
        if game_data["popular_words"][0] not in game_data["guessed_words"]:
            return game_data["popular_words"][0]

    # kui 19 küsimust on küsitud küsime knn-iga kõige lähemat 
    if len(game_data["question_history"]) > 19:
        best_index = probabilities.argmax()
        print("20 küsimuse aeg ehk sõna pakkumine")
        print(words)
        return words[best_index]

    for pop_word in game_data["popular_words"]:
        if pop_word in words and pop_word not in game_data["guessed_words"]:
            return pop_word
    return ""

def unique_question(word):
    df = game_data["dataset"]
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

def back_tracking(history, answers): # leiame viimase jah vastuse ja jätkame sealt edasi 
    print("back_tracking")
    if 1 not in answers:
        last_yes_index = 0
    else:
        last_yes_index = len(answers) - 1 - answers[::-1].index(1)
    df = game_data["dataset_history"][last_yes_index]
    last_question = game_data["question_history"][last_yes_index]
    filtered_df = filter_df(df, last_question, "jah")

    if filtered_df is None or filtered_df.empty:
        remaining_columns = [col for col in game_data["dataset_history"][0] if col not in history and col != "Sõna" and col != "tähtsus"]
    else:
        remaining_columns = [col for col in filtered_df.columns if col not in history and col != "Sõna" and col != "tähtsus" ]
    game_data["no-count"] = 0
    game_data["dataset"] = filtered_df
    #print("valesti vatatud küsimus:", last_question)
    #print( "df suurus: ", filtered_df.shape)
    #print("vastused:", answers)
    #print("küsimused:", game_data["question_history"])
    return remaining_columns, df

## teha funktsioon !!!!!! kui df on tühi siis vaadata mis on knn pakutud sõnad ja nende kohta küsida 
@app.route('/api/answer', methods=['POST'])
def answer():
    print("ANSWER")
    # 4. mängija vastab JAH, EI, EI TEA
    user_answer = request.json.get("answer")

    question = game_data["current_question"]
    df = game_data["dataset"]

    # 5. filtreerime valikut
    df = filter_df(df, question, user_answer)

    print(question)
    print(df.shape)

    # Salvestame uued väärtused
    game_data["dataset"] = df
    game_data["question_history"].append(question)
    if user_answer == "jah":
        game_data["answer_history"].append(1)
    elif user_answer == "ei":
        game_data["answer_history"].append(0)
    else: 
        game_data["answer_history"].append(2)
    game_data["dataset_history"].append(df.copy())
    game_data["popular_words"] = df.loc[df["tähtsus"] == 1, "Sõna"].tolist()
    #print("levinud sõnad:", game_data["popular_words"])

    #print("ennustatud sõna:", words_probability(game_data["dataset_history"][0], game_data["answer_history"])[0])
    game_data["possible_words"] = words_probability(game_data["dataset_history"][0], game_data["answer_history"])
    game_data["selected_word"] = selected_word(df,game_data["possible_words"])

    return ask_question()

@app.route('/api/history', methods=['GET'])
def show_history():
    return jsonify({
        "questions": game_data["question_history"],
        "answers": game_data["answer_history"]
    })

@app.route('/api/undo', methods=['POST'])
def undo_last_question():
    if len(game_data["answer_history"]) > 0:
        # Kui viimane vastus on 0, uuendame no-count väärtust
        if game_data["answer_history"][-1] == 0:
            game_data["no-count"] = max(0, game_data["no-count"] - 1)
        
        game_data["current_question"] = game_data["question_history"][-1]

        # Eemaldame viimase küsimuse ja vastuse ja andmestiku
  
        game_data["answer_history"].pop()
        game_data["question_history"].pop()
        game_data["dataset_history"].pop()

        # Vähendame sammu arvu
        game_data["dataset"] = game_data["dataset_history"][-1]

        return jsonify({"message": "Viimane küsimus tühistatud", "question": game_data["current_question"]})
    else:
        return jsonify({"message": "Ei ole enam küsimusi, mida tagastada"}), 400

@app.route('/api/end', methods=['POST'])
def game_end():
    print("PAKKUSIN SÕNA, OOTAN LÕPP VASTUST")
    user_answer = request.json.get("answer")

    df = game_data["dataset"]
    word = game_data["selected_word"]
    print("end,, selected workd", word)
    if user_answer == "jah":
        game_data["answer_history"].append(1)
        game_data["question_history"].append(f"Kas sõna oli {word}?")
        ending = "Ma võitsin!"
        return jsonify({"outcome": ending})
    elif (user_answer == "ei" or  user_answer == "peaaegu") and len(game_data["question_history"]) >= 20:
        ending = "Sa võitsid!"
        return jsonify({"outcome": ending})
    elif user_answer == "ei" or user_answer == "peaaegu":
        if user_answer == "ei":
            game_data["answer_history"].append(3)
        else:
            game_data["answer_history"].append(4)
        game_data["question_history"].append(f"Kas sõna oli {word}?")
        #remaining_columns = back_tracking(game_data["question_history"][:-2], game_data["answer_history"][:-2])[0]
        df = back_tracking(game_data["question_history"][:-2], game_data["answer_history"][:-2])[1] #pole kindel kas niimoodi võib teha 
        game_data["dataset"] = df 
        game_data["selected_word"] = ""
        game_data["dataset_history"].append(df)
        #next_question = max(remaining_columns, key=lambda col: (df[col].value_counts().get(1, 0)))
        #print("end game'i järgmine küsimus, kas on sama?", next_question)

        # võtan paar sammu tagasi, sest vastus pole isegi lähedal
    
    #game_data["current_question"] = next_question
    return jsonify({"continue": True})



if __name__ == '__main__':
    app.run(debug=True)

# 1. alustame mängu algoritmi
# 2. kontrollitakse kas võib veel küsimust küsida (step < 20)
# 3. küsimuse, mis jagab vastused võimalikult võrdslt pooleks
# 4. mängija vastab JAH, EI, EI TEA
# 5. filtreerime valikut
# 5.1.1 vastus JAH: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele jaatavalt (1)
# 5.1.2 kordame samme 2-4
# 5.2.1 vastus EI: kitsendame valikuid kõigi sõnadega, mis vastasid küsimusele eitavalt (0)
# 5.2.2 kordame samme 2-4
# 5.3.1 vastus EI TEA: arvestame / ei arvesta küsimust küsimute hulk (ei tea kumb on parem valik) 
# 5.3.2 kordame samme 2-4
# 6. kui 20 küsimust saab küsitud kuvame sõna, mille tõenäosus on kõige suurem 
# 7. kui arvuti vastas õigesti, siis tema võit, kui ei siis mängija võit 
# 8. algoritm lõpetab 

# järelikult tuleb järgida ka sõnade tõenäosusi kuidagi
# algoritm võiks ka varem sõna pakkuda, kui see tundub väga tõenäoline (nt võrdleb kas küsida kas tegu on sõnaga või küsib uue küsimuse)

# kuidas vältida, kui mängija kogemata valesti vastab?
# äkki kui vastad 3 küsimusele eitavalt, siis peaks kuidagi 'tagasi' liikuma mõne sammu, sest on oht, et küsimused ei vasta sinu sõnale 
# sest eeldus on ju pigem see, et mängija vastab küsimusele jaatavalt

# mul on ka sõnade 'tähtsus' skaalal 1-5 (1 kõige tähtsam), kus samuti tahaks jälgida, et esmalt uuritakse populaarsemaid sõnu 


# kui on ruumi küsi täpne küsimus enne kui pakud 