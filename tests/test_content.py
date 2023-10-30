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
        cls.list_url = reverse('notes:list', args=None)

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertEqual(object_list[0], self.notes)

    def test_in_author_list_not_other_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        authors_notes = len(object_list.filter(author=self.author))
        self.assertEqual(notes_count, authors_notes)

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
