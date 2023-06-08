from flask import Flask, g, render_template, request, redirect, session
from flask import send_file

import io
import csv
import pickle
import os
from InitData import *
from DecisionTrees import *
from Covers import *

app = Flask(__name__)
app.secret_key = 'my_secret_key' # set a secret key for Flask session
app.config['SESSION_COOKIE_MAX_SIZE'] = 1024 * 1024 * 10  # 10 MB
app.config['SESSION_TYPE'] = 'filesystem'

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TIMEOUT'] = 3600 # 1 hour

# Code to construct decision tree
movies = InitMoviesData25M()
links = InitLinksData25M()
with open('binary_tree.pkl', 'rb') as f:
    #binary tree with depth 15 over 1/10th subset of movielens 25M
    tree = pickle.load(f)
#hardcoded list of 15 most rated items for 1/10th subset of movielens 25M
querie_items_part2 = [318, 356, 296, 593, 2571, 260, 480, 527,
                       2959, 110, 589, 1196, 1, 50, 4993]
#hardcoded list of 20 most rated items for 1/10th subset of movielens 25M
test_items = [1704, 10, 2858, 7361, 5349, 349, 592, 3147,
              293, 253, 1682, 1961, 1206, 2028, 457, 1197, 58559, 4226,
              1265, 1270, 1089, 2628, 858, 33794, 1097,'end']

#admin page to extract data
@app.route("/admin",methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        #check if password is corrent
        if password == 'decisionTree':
            # Load the CSV file and return it as a downloadable file
            with open('emails.csv', 'r') as f:
                #convert file
                csv_data = io.BytesIO(f.read().encode())
            #send files as csv file
            return send_file(csv_data, as_attachment=True,mimetype='text/csv',download_name='data-online.csv')
        else:
            #if pass is invalid return "invalid password"
            return "Invalid password"
    else:
        return render_template("admin.html")
    
#homepage
@app.route("/")
def home():
    return render_template("home.html")

#login page
@app.route("/login", methods=["POST"])
def login():
    #get email
    email = request.form["email"]
    #check if email in emails.csv file
    if email in get_emails():
        #store email in session
        session['email']=email
        # render information page
        return render_template("info.html")
    #if not in file: add to file
    else:
        #
        write_email(email)
        #store email in session
        session['email']=email
        # render information page
        return render_template('info.html')

#present info for first stage
@app.route('/info', methods=['POST','GET'])
def info():
    # redirect to active learning route
    return redirect('/active_learning',code=307)

#present the items of the first stage
@app.route('/active_learning', methods=['POST', 'GET'])
def active_learning():
    #check if first call
    if request.method == 'POST':
        #get seen status
        seen = request.form.get('seen')
        #add to user variable
        seenList = session.get('seen',[])
        if seen == 'seen':
            seenList.append(True)
        else:
            seenList.append(False)
        #change user variable
        session['seen'] = seenList
        #get rating from slider
        rating = float(request.form['rating'])
        #get the ratings of the user
        ratings = session.get('ratingsP1', [])
        #append new rating to ratings
        ratings.append(rating)
        #change user-based var ratinsg
        session['ratingsP1'] = ratings
        #get node for ratings
        node = tree.getNode(ratings)
        #check to see if node exists otherwise redirect
        if node == None:
            return render_template('infopart2.html')
        #get title
        title = movies[movies['movieId'] == node.item]['title'].to_list()[0]
        #get cover image
        cover = getCover(title)
        #get link
        linkid = str(links[links['movieId']==node.item]['imdbId'].to_list()[0])
        link = 'https://www.imdb.com/title/tt'+(7-len(linkid))*'0'+linkid
        #Render the like/dislike template with the next item
        return render_template('active_learning.html', item=title, cover=cover,link=link)
    #if first call just render first item
    else:
        #get title
        currentNode = tree.root
        #create user variable list for ratings and seens
        session['ratingsP1'] = []
        session['seen'] = []
        #get first item to present
        item = currentNode.item
        title = movies[movies['movieId'] == item]['title'].to_list()[0]
        #get cover image
        cover = getCover(title)
        #get link
        linkid = str(links[links['movieId']==item]['imdbId'].to_list()[0])
        link = 'https://www.imdb.com/title/tt'+(7-len(linkid))*'0'+linkid
        #render first query page
        return render_template('active_learning.html', item=title, cover=cover,link=link)

#present second info part
@app.route('/infopart2', methods=['POST','GET'])
def infopart2():
    #redirect to active learning route
    return redirect('/querying',code=307)

#present the items of the first stage
@app.route('/querying', methods=['POST', 'GET'])
def querying():
    #check if first call
    if request.method == 'POST':
        #get seen status
        rated = request.form.get('not_seen')
        #get the ratings of the user
        ratings = session.get('ratingsP2', [])
        if rated == 'true':
            #add None rating
            ratings.append(None)
            #change user-based var ratings
            session['ratingsP2'] = ratings
        else:
            #get rating from slider
            rating = float(request.form['rating'])
            #get the ratings of the user
            ratings = session.get('ratingsP2', [])
            #append new rating to ratings
            ratings.append(rating)
            #change user-based var ratings
            session['ratingsP2'] = ratings
        #get item
        nrRatings = len(ratings)
        #check which item to present, stage2 or test item?
        if nrRatings <15:
            item = querie_items_part2[len(ratings)]
        else:
            item = test_items[len(ratings)-15]
        #check to see if at end, write all results of user to file
        if item == 'end':
            r = session.get('ratingsP1',[])
            s = session.get('seen',[])
            q = session.get('ratingsP2',[])
            e = session.get('email')
            write_ratings(r,s,q,e)
            session.pop('ratingsP1', None)
            session.pop('seen')
            session.pop('ratingsP2')
            session.pop('email')
            return render_template('end.html')
        #get title
        title = movies[movies['movieId'] == item]['title'].to_list()[0]
        #get cover image
        cover = getCover(title)
        #render the rating template with the next item
        return render_template('querying.html', item=title, cover=cover)
    #if first call
    else:
        #get title of item
        item = querie_items_part2[0]
        #create new user variable
        session['ratingsP2'] = []
        title = movies[movies['movieId'] == item]['title'].to_list()[0]
        #get cover image
        cover = getCover(title)
        #render first query page
        return render_template('querying.html', item=title, cover=cover)

#show end screen
@app.route('/end')
def end():
    return render_template('end.html')

#retrieve all emails as list
def get_emails():
    with open("emails.csv", "r") as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]

#write email to file
def write_email(email):
    with open("emails.csv", "a",newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email])

#write all user variables to file
def write_ratings(ratings,seen,queries,email):
    #find correct row
    rows, row_number = None, None
    with open('emails.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    for i, row in enumerate(rows):
        if row[0] == email:
            row_number = i
            break
    #add ratings, seen and queries
    rows[row_number] = [email, ratings, seen, queries]
    with open('emails_temp.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    #replace the original file with the new one
    os.replace('emails_temp.csv', 'emails.csv')

if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
    
