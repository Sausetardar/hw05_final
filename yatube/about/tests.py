from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_authorpage(self):

        response = self.guest_client.get(
            reverse('about:author')
        )
        self.assertEqual(response.status_code, 200)

    def test_techpage(self):

        response = self.guest_client.get(
            reverse('about:tech')
        )
        self.assertEqual(response.status_code, 200)
