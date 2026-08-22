from django.test import SimpleTestCase
from django.urls import resolve, reverse


class StaticPageUrlTests(SimpleTestCase):
    def test_about_page_resolves(self):
        self.assertEqual(resolve('/about/').view_name, 'about')
        self.assertEqual(reverse('about'), '/about/')

    def test_principal_message_page_resolves(self):
        self.assertEqual(resolve('/principal-message/').view_name, 'principal_message')
        self.assertEqual(reverse('principal_message'), '/principal-message/')

    def test_facilities_page_resolves(self):
        self.assertEqual(resolve('/facilities/').view_name, 'facilities')
        self.assertEqual(reverse('facilities'), '/facilities/')
