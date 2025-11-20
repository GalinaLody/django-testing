from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'note-slug'
        }
        cls.user = User.objects.create(username='Кто-то')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')

    def test_user_can_create_note(self):
        """Проверяет, что залогиненный пользователь
        может создавать заметки.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_anonimous_cant_create_note(self):
        """Проверяет, что анонимный пользователь
        не может создавать заметки.
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        """Проверяет, что нельзя создать заметки
        с одинаковыми слагами.
        """
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug',
            author=self.user
        )
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Проверяет, что при создании заметки с пустым полем для слага
        слаг формируетс автоматически из названия.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDeleteNote(TestCase):
    NEW_NOTE_TEXT = 'Обновленный текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой пользователь')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'slug'
        }

    def test_author_can_edit_note(self):
        """Проверяет, что пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_not_author_cant_edit_note(self):
        """Проверяет, пользователь не может редактировать чужие заметки."""
        response = self.not_author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get()
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        """Проверяет, что пользователь может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_not_author_cant_delete_note(self):
        """Проверяет, что пользователь не ожет удалять чужие заметки."""
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
