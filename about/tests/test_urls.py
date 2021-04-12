from django.test import Client, TestCase


class StaticViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_urls_exist_at_desired_location(self):
        """Проверка доступности адресов приложения about."""
        urls_names = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_static_pages_urls_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения about."""
        urls_templates_names = {
            '/about/author/': 'author.html',
            '/about/tech/': 'tech.html'
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
