from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.base_tests import (
    CommonBaseTest,
    ADD_NOTE_URL,
    EDIT_NOTE_URL,
    NOTE_LIST_URL
)


User = get_user_model()


class TestDetailNote(CommonBaseTest):
    """Набор тестов, проверяющих работу заметки."""

    def test_note_in_notes_list_author(self):
        """Проверяет, что отдельная заметка
        передается в список заметок автора.
        """
        self.assertIn(
            self.note,
            self.author_client.get(NOTE_LIST_URL).context['object_list']
        )
        note_from_page = (
            self.author_client
            .get(NOTE_LIST_URL)
            .context['object_list'][0]
        )
        self.assertEqual(note_from_page.title, self.note.title)
        self.assertEqual(note_from_page.text, self.note.text)
        self.assertEqual(note_from_page.slug, self.note.slug)
        self.assertEqual(note_from_page.author, self.note.author)

    def test_note_not_in_notes_list_not_author(self):
        """Проверяет, что отдельная заметка не передается в список заметок
        другого авторизованного пользователя-не автора.
        """
        self.assertNotIn(
            self.note,
            self.reader_client.get(NOTE_LIST_URL).context['object_list']
        )

    def test_add_and_create_pages_has_form(self):
        """Проверяет наличие формы на страницах добавления и редактирования
        заметки.
        """
        urls = (
            ADD_NOTE_URL,
            EDIT_NOTE_URL,
        )
        for url in urls:
            with self.subTest(url):
                self.assertIsInstance(
                    self.author_client.get(url).context.get('form'),
                    NoteForm
                )
