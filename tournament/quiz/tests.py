from django.test import TestCase
from django.db import models
from .models import Category, Tournament, User, UserTournament
from .questions import QUESTIONS_GEOGRAPHY, QUESTIONS_SPORTS
from django.db.models import Max
from datetime import date
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from random_username.generate import generate_username
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class QuizModelTest(TestCase):
    def setUp(self):
        self.category_geography = self.create_category('Geography', 1)
        self.category_sports = self.create_category('Sports', 2)
        self.tournament1 = self.create_tournament('Test_Tournament1', 'Easy', self.category_geography.id, '2020-06-25', '2020-06-26', QUESTIONS_GEOGRAPHY)
        self.tournament2 = self.create_tournament('Test_Tournament2', 'Easy', self.category_sports.id, '2020-06-19', '2020-06-24', QUESTIONS_SPORTS)
        self.tournament3 = self.create_tournament('Test_Tournament3', 'Hard', self.category_sports.id, '2020-06-17', '2020-06-22', QUESTIONS_SPORTS)
        self.user1 = self.create_user('TestUser1', 'P@ssw0rd123')
        self.user2 = self.create_user('TestUser2', 'P@ssw0rd123')

    def test_tournament_name(self):
        tournament = Tournament.objects.get(name='Test_Tournament1')
        self.assertEqual(tournament.name, 'Test_Tournament1')

    def test_tournament_category_name(self):
        tournament = Tournament.objects.get(name='Test_Tournament1')
        self.assertEqual(tournament.category.category, 'Geography')
        self.assertEqual(tournament.category.key, 1)

    def test_user_name(self):
        user = User.objects.get(username='TestUser1')
        interests = user.interests.all()
        interest_geography = interests[0]
        interest_sports = interests[1]
        self.assertEqual(user.username, 'TestUser1')
        self.assertEqual(interest_geography.category, 'Geography')
        self.assertEqual(interest_sports.category, 'Sports')

    def test_top_players(self):
        self.player_quiz()
        top_players = self.tournament1.top_players
        self.assertEqual(json.loads(top_players)[0]['player'], 'TestUser1')

    def test_total_taken(self):
        self.player_quiz()
        self.assertEqual(self.tournament1.total_taken, 2)

    def test_high_score(self):
        self.player_quiz()
        self.assertEqual(self.tournament1.high_score, 6)

    def test_ongoing(self):
        tournaments = Tournament.ongoing()
        self.assertEqual(len(tournaments), 1)
        self.assertLessEqual(tournaments[0].start_date, date.today())

    def test_upcoming(self):
        tournaments = Tournament.upcoming()
        self.assertEqual(len(tournaments), 1)
        self.assertGreaterEqual(tournaments[0].start_date, date.today())

    def test_past(self):
        tournaments = Tournament.past()
        self.assertEqual(len(tournaments), 1)
        self.assertLess(tournaments[0].end_date, date.today())

    def test_takenby(self):
        self.player_quiz()
        self.assertEqual(len(self.tournament1.taken_by), 2)
        user = UserTournament.objects.get(id=1)
        self.assertEqual(user.user.username, 'TestUser1')
    
    def create_category(self, category_name, key):
        return Category.objects.create(category=category_name, key=key)

    def create_tournament(self, name, difficulty, category_id, start_date, end_date, questions):
        return Tournament.objects.create(name=name, difficulty=difficulty, category_id=category_id, start_date=start_date, end_date=end_date, questions=questions)

    def create_user(self, username, password):
        user = User.objects.create(username=username, password=password)
        user.save()
        user.interests.add(self.category_geography)
        user.interests.add(self.category_sports)
        return user

    def player_quiz(self):
        user1_answers = self.user_answers(4)
        user2_answers = self.user_answers(5)
        UserTournament.objects.create(tournament_id=self.tournament1.id, user_id=self.user1.id, score=6, answers=user1_answers)
        UserTournament.objects.create(tournament_id=self.tournament1.id, user_id=self.user1.id, score=5, answers=user2_answers)
    
    def user_answers(self, number_of_wrong_answers):
        user_answers = []
        question_number = 0
        for question in QUESTIONS_GEOGRAPHY:
            question_number += 1
            if question_number > number_of_wrong_answers:
                question['user_answer'] = None
            else:
                question['user_answer'] = question['correct_answer']
            user_answers.append(question)
        return user_answers

    def tearDown(self):
        self.category_geography = None
        self.category_sports = None
        self.tournament1 = None
        self.tournament2 = None
        self.tournament3 = None
        self.user1 = None
        self.user2 = None

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/signup")
        self.random_user = generate_username(1)

    def test_register_user(self):
        username = self.driver.find_element_by_css_selector("#id_username")
        username.send_keys(self.random_user[0])
        password1 = self.driver.find_element_by_css_selector("#id_password1") 
        password1.send_keys("P@ssw0rd123")
        password2 = self.driver.find_element_by_css_selector("#id_password2")    
        password2.send_keys("P@ssw0rd123")
        interest1 = self.driver.find_element_by_css_selector("#id_interests_0")
        interest1.click()  
        interest2 = self.driver.find_element_by_css_selector("#id_interests_1")  
        interest2.click()
        signup = self.driver.find_element_by_css_selector("#signup")
        signup.send_keys(Keys.RETURN)
        user = self.driver.find_element_by_css_selector('#navbarDropdown').get_attribute("text")
        self.assertEqual(user, self.random_user[0])


class CreateTournamentTest(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("http://127.0.0.1:8000/login") 

    def test_user_login(self):
        username = self.driver.find_element_by_css_selector("#id_username")
        username.send_keys("admin")
        password = self.driver.find_element_by_css_selector("#id_password") 
        password.send_keys("P@ssw0rd123")
        login = self.driver.find_element_by_css_selector("#login")  
        login.click()
        self.driver.find_element_by_css_selector("#tournaments").click()
        self.driver.find_element_by_css_selector("#newTournament").click()
        try:
            myElem = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, '#name')))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")
        tournament_name = self.driver.find_element_by_css_selector("#name")
        tournament_name.send_keys("Tournament6")
        self.driver.find_element_by_css_selector("#start_date").send_keys("26/06/2020")
        self.driver.find_element_by_css_selector("#end_date").send_keys("29/06/2020")
        self.driver.find_element_by_css_selector("#save").click()
        try:
            myElem = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, "//td[contains(text(),'Tournament6')]")))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")
        available = False
        try:
            self.driver.find_element_by_xpath("//td[contains(text(),'Tournament6')]")
            available = True
        except:
            available = False
        self.assertEqual(available, True)
        

