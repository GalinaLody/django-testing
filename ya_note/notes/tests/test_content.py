from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestDetailNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """Проверяет, что отдельная заметка передается в список заметок автора
        и не передается в список заметок
        другого авторизованного пользователя-не автора. """
        note_in_list = (
            (self.author, True),
            (self.not_author, False),
        )
        for user, note_status in note_in_list:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_status)

    def test_add_and_create_pages_has_form(self):
        """Проверяет наличие формы на страницах добавления и редактирования
        заметки."""
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
