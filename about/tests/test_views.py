from django.test import Client, TestCase
from django.urls import reverse


class StaticViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_acessible_by_name(self):
        """URL, генерируемые при помощи имени about, доступны."""
        static_pages_names = [
            'about:author',
            'about:tech'
        ]
        for page in static_pages_names:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page))
                self.assertEqual(response.status_code, 200)

    def test_static_pages_use_correct_template(self):
        """При запросе к urls приложения about
        применяется соответствующие шаблоны."""
        urls_templates_names = {
            'about:author': 'author.html',
            'about:tech': 'tech.html'
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
