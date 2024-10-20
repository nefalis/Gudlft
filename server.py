import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    """
    Load the list of clubs from a JSON file.
    """
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        for club in listOfClubs:
            club['points'] = int(club['points'])
        return listOfClubs


def loadCompetitions():
    """
    Load the list of competitions from a JSON file.
    """
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for competition in listOfCompetitions:
            competition['numberOfPlaces'] = int(competition['numberOfPlaces'])
        return listOfCompetitions


def saveClubs(clubs):
    """
    Save the updated list of clubs to the JSON file.
    """
    with open('clubs.json', 'w') as f:
        json.dump({'clubs': clubs}, f, indent=4)


def saveCompetitions(competitions):
    """
    Save the updated list of competitions to the JSON file.
    """
    with open('competitions.json', 'w') as f:
        json.dump({'competitions': competitions}, f, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

# Load competitions and clubs from JSON files.
competitions = loadCompetitions()
clubs = loadClubs()

# Create dictionaries for quick access.
clubs_dict = {club['name']: club for club in clubs}
competitions_dict = {competition['name']: competition for competition in competitions}


@app.route('/')
def index():
    """
    Route for the homepage.
    """
    return render_template('index.html')


@app.route('/pointsDisplay')
def pointsDisplay():
    """
    Route to display the points of all clubs.
    """
    return render_template('pointsDisplay.html', clubs=clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    """
    Route to display a summary for the logged-in club.
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
    Route to book places for a competition.
    """
    foundClub = clubs_dict.get(club)
    foundCompetition = competitions_dict.get(competition)

    # Check if the competition is in the past.
    competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("This competition has already ended.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    # If both club and competition exist, proceed to the booking page.
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    """
    Route to handle the purchase of competition places.
    """
    competition_name = request.form.get('competition')
    club_name = request.form.get('club')
    places_required = request.form.get('places')

    # Check if the club and competition exist.
    competition = competitions_dict.get(competition_name)
    club = clubs_dict.get(club_name)

    if not competition or not club:
        flash("Invalid club or competition.")
        return redirect(url_for('index'))

    # Validate the number of requested places.
    if not places_required.isdigit() or int(places_required) <= 0:
        flash("Invalid number of places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    places_required = int(places_required)

    # Check if the competition is still active.
    if not is_competition_active(competition):
        flash("You cannot book places for a competition that has already ended.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Ensure the requested places don't exceed the 12-place limit.
    if places_required > 12:
        flash("You cannot book more than 12 places per competition.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the competition has enough available places.
    if not has_sufficient_places(competition, places_required):
        flash("Not enough places available.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the club has enough points.
    if not has_sufficient_points(club, places_required):
        flash("You don't have enough points.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Update the number of places and points.
    process_booking(competition, club, places_required)

    flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=competitions)


def is_competition_active(competition):
    """
    Checks if the competition is still active.
    """
    competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    return competition_date >= datetime.now()


def has_sufficient_points(club, points_required):
    """
    Checks if the club has enough points to book the required places.
    """
    print(f"Checking points: {club['points']} available, {points_required} required.")
    return int(club['points']) >= points_required


def has_sufficient_places(competition, places_required):
    """
    Checks if the competition has enough available places.
    """
    print(f"Checking places: {competition['numberOfPlaces']} available, {places_required} required.")
    return int(competition['numberOfPlaces']) >= places_required


def process_booking(competition, club, places_required):
    """
    Updates the number of available places in the competition and the club's points.
    """
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
    club['points'] = int(club['points']) - places_required

    saveClubs(clubs)
    saveCompetitions(competitions)


@app.route('/logout')
def logout():
    """
    Route to handle user logout.
    """
    return redirect(url_for('index'))
