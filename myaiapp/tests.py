from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardTests(TestCase):
    def test_dashboard_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class ChatbotTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_chatbot_requires_login(self):
        response = self.client.get(reverse('chatbot:chatbot'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_chatbot_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('chatbot:chatbot'))
        self.assertEqual(response.status_code, 200)

class ImageChatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_image_chat_requires_login(self):
        response = self.client.get(reverse('image_chat:chat'))
        self.assertEqual(response.status_code, 302)

    def test_image_chat_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('image_chat:chat'))
        self.assertEqual(response.status_code, 200)
