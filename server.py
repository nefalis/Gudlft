import json
from datetime import datetime
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions
    
def saveClubs(clubs):
    with open('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f, indent=4)

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pointsDisplay')
def pointsDisplay():
    return render_template('pointsDisplay.html', clubs=clubs)

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form.get('email')
    if not email:
        flash("Email is required.")
        return redirect(url_for('index'))

    club = next((club for club in clubs if club['email'] == email), None)
    if club is None:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]

    # Vérifier si la compétition est dans le passé
    competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("This competition has already ended.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():

    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]

    if not competition or not club:
        flash("Invalid club or competition.")
        return redirect(url_for('index'))
    
    # Vérifier si la compétition est dans le passé
    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("You cannot book places for a competition that has already ended.")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    placesRequired = int(request.form['places'])

    # Vérification si le nombre de places demandées dépasse la limite de 12
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification si le club a suffisamment de points
    pointsRequired = placesRequired
    if pointsRequired > int(club['points']):
        flash(f"You don't have enough points.")

    # Vérification si la compétition a suffisamment de places disponibles
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Not enough places available.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Mettre à jour le nombre de places et les points
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points']) - pointsRequired

    # Enregistrer les modifications
    saveClubs(clubs)

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

