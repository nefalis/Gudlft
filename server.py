import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    """
    Load the list of clubs from a JSON file
    """
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        for club in listOfClubs:
            club['points'] = int(club['points'])
        return listOfClubs


def loadCompetitions():
    """
    Load the list of competitions from a JSON file
    """
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def saveClubs(clubs):
    """
    Save the updated list of clubs to the JSON file
    """
    with open('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f, indent=4)

def saveCompetitions(competitions):
    """Save the updated list of competitions to the JSON file."""
    with open('competitions.json', 'w') as f:
        json.dump({'competitions': competitions}, f, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

# Load competitions and clubs from JSON files
competitions = loadCompetitions()
clubs = loadClubs()

# Create dictionaries for quick access
clubs_dict = {club['name']: club for club in clubs}
competitions_dict = {competition['name']: competition for competition in competitions}


@app.route('/')
def index():
    """
    Route for the homepage
    """
    return render_template('index.html')


@app.route('/pointsDisplay')
def pointsDisplay():
    """
    Route to display the points of all clubs
    """
    return render_template('pointsDisplay.html', clubs=clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    """
    Route to display a summary for the logged-in club
    """
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
def book(competition, club):
    """
    Route to book places for a competition
    """
    foundClub = clubs_dict.get(club)
    foundCompetition = competitions_dict.get(competition)

    # Check if the competition is in the past
    competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("This competition has already ended.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    # If both club and competition exist, proceed to the booking page
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    """
    Route to handle the purchase of competition places
    """
    competition = competitions_dict.get(request.form['competition'])
    club = clubs_dict.get(request.form['club'])

    if not competition or not club:
        flash("Invalid club or competition.")
        return redirect(url_for('index'))

    # Check if the competition is in the past
    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("You cannot book places for a competition that has already ended.")
        return render_template('welcome.html', club=club, competitions=competitions)

    placesRequired = int(request.form['places'])

    # Check if the number of requested places exceeds the 12-place limit
    if placesRequired > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the club has enough points
    pointsRequired = placesRequired
    if pointsRequired > int(club['points']):
        flash("You don't have enough points.")

    # Check if the competition has enough available places
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Not enough places available.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Update the number of places and points
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points']) - pointsRequired

    saveClubs(clubs)
    saveCompetitions(competitions)

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/logout')
def logout():
    """
    Route to handle user logout
    """
    return redirect(url_for('index'))
