from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.base_tests import (
    CommonBaseTest,
    ADD_NOTE_URL,
    DELETE_NOTE_URL,
    EDIT_NOTE_URL,
    NOTE_SUCCESS_PAGE_URL,
    USER_LOGIN_URL
)


User = get_user_model()


class TestActionsNote(CommonBaseTest):
    """Набор тестов,
    проверяющий все основные действия пользователя с заметками:
    создание, редактирование и удаление.
    """

    def test_user_can_create_note(self):
        """Проверяет, что залогиненный пользователь
        может создавать заметки.
        """
        initial_number_notes = Note.objects.count()
        self.assertRedirects(
            self.user_client.post(ADD_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        self.assertEqual(Note.objects.count(), initial_number_notes + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonimous_cant_create_note(self):
        """Проверяет, что анонимный пользователь
        не может создавать заметки.
        """
        initial_number_notes = Note.objects.count()
        self.assertRedirects(
            self.client.post(ADD_NOTE_URL, data=self.form_data),
            f'{USER_LOGIN_URL}?next={ADD_NOTE_URL}'
        )
        self.assertFalse(
            Note.objects.filter(
                slug=self.form_data['slug']
            ).exists()
        )
        self.assertEqual(Note.objects.count(), initial_number_notes)

    def test_not_unique_slug(self):
        """Проверяет, что нельзя создать заметки
        с одинаковыми слагами.
        """
        initial_number_notes = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        self.assertFormError(
            form=(
                self.author_client
                .post(ADD_NOTE_URL, data=self.form_data)
                .context['form']
            ),
            field='slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), initial_number_notes)

    def test_empty_slug(self):
        """Проверяет, что при создании заметки с пустым полем для слага
        слаг формируетс автоматически из названия.
        """
        initial_number_notes = Note.objects.count()
        self.form_data.pop('slug')
        self.assertRedirects(
            self.author_client.post(ADD_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        self.assertEqual(Note.objects.count(),  initial_number_notes + 1)
        new_note = Note.objects.get(slug=slugify(self.form_data['title']))
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Проверяет, что пользователь может редактировать свои заметки."""
        initial_number_notes = Note.objects.count()
        self.assertRedirects(
            self.author_client.post(EDIT_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        self.assertEqual(Note.objects.count(),  initial_number_notes)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_author_cant_edit_note(self):
        """Проверяет, пользователь не может редактировать чужие заметки."""
        self.assertEqual(
            self.not_author_client.post(
                EDIT_NOTE_URL,
                data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        edited_note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.text, edited_note.text)
        self.assertEqual(self.note.title, edited_note.title)
        self.assertEqual(self.note.slug, edited_note.slug)
        self.assertEqual(edited_note.author, self.author)

    def test_author_can_delete_note(self):
        """Проверяет, что пользователь может удалять свои заметки."""
        initial_number_notes = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(DELETE_NOTE_URL),
            NOTE_SUCCESS_PAGE_URL
        )
        self.assertEqual(Note.objects.count(), initial_number_notes - 1)

    def test_not_author_cant_delete_note(self):
        """Проверяет, что пользователь не может удалять чужие заметки."""
        initial_number_notes = Note.objects.count()
        self.assertEqual(
            self.not_author_client.delete(DELETE_NOTE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), initial_number_notes)
        note_after_delete = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note_after_delete.title, self.note.title)
        self.assertEqual(note_after_delete.text, self.note.text)
        self.assertEqual(note_after_delete.slug, self.note.slug)
        self.assertEqual(note_after_delete.author, self.author)
