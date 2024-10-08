from locust import HttpUser, between, task

class MyUser(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 3)

    @task
    def index(self):
        # Tester la page d'accueil
        with self.client.get("/", catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(f"Le temps de chargement dépasse 5 secondes : {response.elapsed.total_seconds()}s")
            else:
                response.success()

    @task
    def points_display(self):
        # Tester l'affichage des points
        with self.client.get("/pointsDisplay", catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(f"Le temps de chargement dépasse 5 secondes : {response.elapsed.total_seconds()}s")
            else:
                response.success()

    @task
    def login_and_show_summary(self):
        # Tester le login et l'affichage du résumé
        email = "test@example.com"
        with self.client.post("/showSummary", data={"email": email}, catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(f"Le temps de chargement dépasse 5 secondes : {response.elapsed.total_seconds()}s")
            else:
                response.success()

    @task
    def book_competition(self):
        # Tester la réservation d'une place
        competition_name = "Spring Festival"
        club_name = "Test Club"
        with self.client.get(f"/book/{competition_name}/{club_name}", catch_response=True) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure(f"Le temps de mise à jour dépasse 2 secondes : {response.elapsed.total_seconds()}s")
            else:
                response.success()

    @task
    def purchase_places(self):
        # Tester l'achat de places
        competition_name = "Spring Festival"
        club_name = "Test Club"
        places = 2
        with self.client.post("/purchasePlaces", data={"competition": competition_name, "club": club_name, "places": places}, catch_response=True) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure(f"Le temps de mise à jour dépasse 2 secondes : {response.elapsed.total_seconds()}s")
            else:
                response.success()