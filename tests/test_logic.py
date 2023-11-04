from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'Adress'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иваныч')
        cls.not_author = User.objects.create(username='Петр Петрович')
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст',
                                        slug='Adress',
                                        author=cls.author
                                        )
        cls.url = reverse('notes:add', args=None,)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.TEXT,
                         'slug': cls.SLUG}
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))

    def test_anonymous_user_cant_create_note(self):  
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        notes = Note.objects.last()
        self.assertEqual(notes.title, self.TITLE)
        self.assertEqual(notes.text, self.TEXT)
        self.assertEqual(notes.slug, self.SLUG)
        self.assertEqual(notes.author, self.author)


class TestSameSlug(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = ''

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иваныч')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)        
        cls.note = Note.objects.create(title=cls.TITLE,
                                       text=cls.TEXT,
                                       slug=cls.SLUG, 
                                       author=cls.author)
        cls.url = reverse('notes:add', args=None,)
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.author}

    def test_cant_same_slug_twice(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        self.auth_client.post(self.url, data=self.form_data)
        self.note.refresh_from_db()
        slug = slugify(self.TITLE)
        self.assertEqual(self.note.slug, slug)


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_author = User.objects.create(username='Другой автор')
        cls.other_author_client = Client()
        cls.other_author_client.force_login(cls.other_author)
        cls.authors_note = Note.objects.create(title=cls.TITLE,
                                               text=cls.TEXT,
                                               slug=cls.SLUG,
                                               author=cls.author)
        cls.edit_note_url = reverse('notes:edit',
                                    args=(cls.authors_note.slug,))
        cls.delete_note_url = reverse('notes:delete',
                                      args=(cls.authors_note.slug,))
        cls.form_data = {'title': 'Другой_заголовок',
                         'text': 'Другой текст',
                         'slug': 'other_slug',
                         'author': cls.author}

    def test_author_can_delete_own_note(self):
        self.author_client.delete(self.delete_note_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_author_cant_delete_note_of_author(self):
        response = self.other_author_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_own_note(self):
        self.author_client.post(self.edit_note_url, data=self.form_data)
        self.authors_note.refresh_from_db()
        self.assertEqual(self.authors_note.title, self.form_data['title'])
        self.assertEqual(self.authors_note.text, self.form_data['text'])
        self.assertEqual(self.authors_note.slug, self.form_data['slug'])
        self.assertEqual(self.authors_note.author, self.form_data['author'])

    def test_other_author_cant_edit_authors_note(self):
        response = self.other_author_client.post(self.edit_note_url,
                                                 data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.authors_note.refresh_from_db()
        self.assertEqual(self.authors_note.title, self.TITLE)
        self.assertEqual(self.authors_note.text, self.TEXT)
        self.assertEqual(self.authors_note.slug, self.SLUG)
        self.assertEqual(self.authors_note.author, self.author)
