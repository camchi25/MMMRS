# see bottom for notes
# most of the homework i just put into the project so I'm gonna submit the project for the homework

import csv
# import os
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import confusion_matrix
from flask import Flask, request, render_template
import matplotlib.pyplot as plt

# gets dataframe of a single song with the song name (i'm having trouble with .loc so it only looks for the song name and not the artist name for now)
def get_song_elements(songname, artist, fileName):
    df = pd.read_csv(fileName, encoding= 'unicode_escape')
    df = df.loc[df["name"] == songname]
    this = 0
    songthere = False
    for index, i in df.iterrows():
        this = i
        songthere = True
        break
    if songthere == False:
        return "SONG NOT AVAILABLE"
    return this

# 
def collect_user_preferences(fileName, song, mashupFileName):
    df = pd.read_csv(fileName, encoding= 'unicode_escape').sample(10)
    preferences = []
    for index, row in df.iterrows():
        pref = []
        test = input("Do you like the mash-up of \"" + str(song["name"]) + "\" by " + str(song["artists"]) + " and \"" + str(row["name"]) + "\" by " + str(row["artists"]) + "? (yes/no)").lower()
        pref.append(song["name"])
        pref.append(song["artists"])
        pref.append(row["name"])
        pref.append(row["artists"])
        if test == 'yes':
            pref.append(1)
        else:
            pref.append(0)
        preferences.append(pref)
    
    with open(mashupFileName, 'a', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for i in preferences:
            writer.writerow(i)

def train_model(fileName, mashupFileName, graphName, alsotest = True, song = ""):
    df = pd.read_csv(fileName, encoding= 'unicode_escape')
    mdf = pd.read_csv(mashupFileName, encoding= 'unicode_escape')
    features = list(df.columns)

    features.remove("id")
    features.remove("artists")
    features.remove("name")
    x = []
    y = []
    rsq = 0
    mse = 0

    for index, i in mdf.iterrows():
        song1 = df.loc[df['name'] == i[0]]
        for index, j in song1.iterrows():
            song1 = j
            break
        song2 = df.loc[df['name'] == i[2]]
        for index, j in song2.iterrows():
            song2 = j
            break
        
        # takes difference of 
        thing = []
        accepted = ["acousticness","danceability","duration_ms","energy","instrumentalness","liveness","loudness","popularity","speechiness","tempo"]
        badsong = False
        for feature in features:
            try:
                if feature in accepted:
                    thing.append(abs(float(song1[feature]) - float(song2[feature])))
            except:
                badsong = True
                break
        if badsong == False:
            x.append(thing)
            y.append(i[4]) # index for if mashup works
    model = LinearRegression()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2) 
    model.fit(x_train, y_train)
    if alsotest == True:
        
        y_pred = model.predict(x_test)
        mse = sklearn.metrics.mean_squared_error(y_test, y_pred)
        rsq = sklearn.metrics.r2_score(y_test, y_pred)
        print("===\nMean Squared Error: " + str(mse))
        print("R-Squared Error: " + str(rsq))

        y_predbinary = [1 if pred >= 0.32 else 0 for pred in y_pred]
        tn, fp, fn, tp = confusion_matrix(y_test, y_predbinary).ravel()
        
        plt.bar(['True Positives', 'False Positives', 'True Negatives', 'False Negatives'], [tp, fp, tn, fn])
        plt.xlabel('Categories')
        plt.ylabel('Count')
        plt.title('Confusion Matrix')
        plt.savefig(graphName)
        plt.show()

    else:
        df = pd.read_csv(fileName, encoding= 'unicode_escape').sample(100)
        features = list(df.columns)

        x = []
        y = []
        goodsongs = []
        goodsongnames = []

        scores = {}
        for index, compare_song in df.iterrows():
            thing = []
            accepted = ["acousticness","danceability","duration_ms","energy","instrumentalness","liveness","loudness","popularity","speechiness","tempo"]
            badsong = False
            for feature in features:
                try:
                    if feature in accepted:
                        thing.append(abs(float(song[feature]) - float(compare_song[feature])))
                except:
                    badsong = True
                    break
            if badsong == False:
                goodsongs.append(thing)
                goodsongnames.append(compare_song["name"])
        prediction = model.predict(goodsongs)
        for i in range(len(prediction)):
            scores[goodsongnames[i]] = prediction[i]
        
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:10]
        top_10_songs = [item[0] for item in sorted_scores]
        top_10_scores = [item[1] for item in sorted_scores]

        # Plot the top 10 scores in a bar chart
        plt.bar(top_10_songs, top_10_scores)
        plt.xlabel('Songs')
        plt.ylabel('Scores')
        plt.title('Top 10 Predicted Scores')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(graphName)
        plt.show()
    return [rsq,mse]
    
def insert_song(songname, artist, fileName):
    df = pd.read_csv(fileName)
    features = list(df.columns)
    inp = [input(f"===\n{feature}? ") for feature in features]
    with open(fileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(inp)

def insert_mashup(fileName, mashupFileName):
    insertthis = []
    with open(fileName, 'r') as csvfile:
        reader = list(csv.reader(csvfile))
        for i in range(2):
            songname = input("===\nSong name: ")
            artistname = input("Artist: ")
            checkifinfile = False
            if reader and reader[0]:
                for a in reader:
                    if songname in a[0] and artistname in a[1]:
                        checkifinfile = True
                        insertthis.append(a[0])
                        insertthis.append(a[1])
                        break
            if not checkifinfile:
                insert_song(songname, artistname, fileName)
                insertthis.append(songname)
                insertthis.append(artistname)
    insertthis.append(1)
    with open(mashupFileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(insertthis)
        
def hello_world():
    # will change later
    fileName = "data/data.csv"
    mashupFileName = "mashupdata.csv"
    graphName = "templates/project_files/graph.png"
    graph2Name = "templates/project_files/graph2.png"

    print("Welcome to the Music Mashup Recommendation System Debug Menu!")
    exitt = False
    while exitt == False:
        print("1 - Insert song with data")
        print("2 - Train Model")
        print("3 - Insert liked mashup")
        print("4 - Use Model")
        print("5 - Exit")
        s = input("Input a number to select: ")
        if s == "1":
            songname = input("===\nSong name: ")
            artistname = input("===\nArtist: ")
            insert_song(songname, artistname, fileName)
        elif s == "2":
            songname = input("===\nSong name: ")
            artistname = input("===\nArtist: ")
            songdata = get_song_elements(songname, artistname, fileName)
            collect_user_preferences(fileName, songdata, mashupFileName)
            model = train_model(fileName, mashupFileName, graphName, True)
        elif s == "3":
            insert_mashup(fileName,mashupFileName)
        elif s == "4":
            songname = input("===\nSong name: ")
            artistname = input("===\nArtist: ")
            songdata = get_song_elements(songname, artistname, fileName)
            train_model(fileName, mashupFileName, graph2Name, False, songdata)
        else:
            exitt = True
    print("Thank you for using MMRS")

app = Flask(__name__)
graphs = False
@app.route('/')
def main():
    return render_template('project.html', msg = "Enter your songs...", graphs = graphs)
@app.route('/', methods=['POST'])
def main_post():
    graphs = True
    fileName = "data/data.csv"
    mashupFileName = "mashupdata.csv"
    graphName = "templates/project_files/graph.png"
    graph2Name = "templates/project_files/graph2.png"

    songname = request.form['text']
    songdata = get_song_elements(songname,"",fileName)
    if type(songdata) != str:
        stuff = train_model(fileName, mashupFileName, graph2Name, False, songdata)
        return render_template('project.html', msg = "We found some songs for you based on " + str(songname) + "!\n - MSQ: " + str(stuff[1]) + "\n - RSE: " + str(stuff[0]), graphs = graphs)
    else:
        return "This song is not available in this database. Try again or check for spelling/capitalization errors."

print("Welcome to the Music Mashup Recommendation System!")
print("1 - Debug Menu")
print("2 - Open the website")
s = input("Input a number to select: ")
if s == "1":
    hello_world()
elif s == "2":
    graphs = False
    app.run()
else:
    print("Goodbye")
