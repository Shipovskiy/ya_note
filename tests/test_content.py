from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иваныч')
        cls.not_author = User.objects.create(username='Петр Петрович')
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        slug='Adress',
                                        author=cls.author
                                        )
        cls.list_url = reverse('notes:list', args=(cls.notes.slug,))

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),)
        for name, args in urls:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
