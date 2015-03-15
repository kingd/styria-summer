from django.core.urlresolvers import reverse
from django.test import TestCase


class FeeddlerTest(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_add_feed(self):
        link = 'http://www.24sata-test.hr/feeds/najnovije.xml'
        data = {'link': link, 'is_active': True}
        self.client.post(reverse('add_feed'), data)
        response = self.client.get(reverse('index'))
        self.assertTrue(link in response.content)
