from locust import HttpUser, between, task


class MyUser(HttpUser):
    host = "http://127.0.0.1:5000"
    wait_time = between(1, 5)

    @task
    def index(self):
        # Tester la page d'accueil
        self.client.get("/")

    @task
    def points_display(self):
        # Tester l'affichage des points
        self.client.get("/pointsDisplay")

    @task
    def book_competition(self):
        # Tester la réservation d'une place
        competition_name = "Spring Festival"
        club_name = "Test Club"
        self.client.get(f"/book/{competition_name}/{club_name}")

    @task
    def purchase_places(self):
        # Tester l'achat de places
        competition_name = "Spring Festival"
        club_name = "Test Club"
        self.client.post("/purchasePlaces", data={
            "competition": competition_name,
            "club": club_name,
            "places": "5"}
            )

    @task
    def logout(self):
        self.client.get("/logout")
