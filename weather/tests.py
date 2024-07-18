from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import City, SearchHistory

class WeatherViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_weather_view_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('weather_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

    def test_weather_view_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('weather_view'), {'city_name': 'Berlin'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/weather.html')
        self.assertIn('weather_data', response.context)

    def test_search_count_api(self):
        self.client.login(username='testuser', password='testpassword')
        City.objects.create(name='Berlin')
        response = self.client.get(reverse('search_count_api'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), [])

    def test_search_count_increment(self):
        self.client.login(username='testuser', password='testpassword')
        city = City.objects.create(name='Berlin')
        SearchHistory.objects.create(user=self.user, city=city, search_count=1)
        response = self.client.post(reverse('weather_view'), {'city_name': 'Berlin'})
        self.assertEqual(SearchHistory.objects.get(city=city, user=self.user).search_count, 2)
