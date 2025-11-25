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
    REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL
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
        old_slugs = list(Note.objects.values_list('slug', flat=True))
        self.assertRedirects(
            self.reader_client.post(ADD_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        new_notes = Note.objects.exclude(slug__in=old_slugs)
        self.assertEqual(new_notes.count(), 1)
        new_note = new_notes.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.reader)

    def test_anonimous_cant_create_note(self):
        """Проверяет, что анонимный пользователь
        не может создавать заметки.
        """
        old_slugs = list(Note.objects.values_list('slug', flat=True))
        self.assertRedirects(
            self.client.post(ADD_NOTE_URL, data=self.form_data),
            REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL
        )
        new_notes = Note.objects.exclude(slug__in=old_slugs)
        self.assertEqual(new_notes.count(), 0)

    def test_not_unique_slug(self):
        """Проверяет, что нельзя создать заметки
        с одинаковыми слагами.
        """
        old_slugs = list(Note.objects.values_list('slug', flat=True))
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
        new_notes = Note.objects.exclude(slug__in=old_slugs)
        self.assertEqual(new_notes.count(), 0)

    def test_empty_slug(self):
        """Проверяет, что при создании заметки с пустым полем для слага
        слаг формируетс автоматически из названия.
        """
        old_slugs = list(Note.objects.values_list('slug', flat=True))
        self.form_data.pop('slug')
        self.assertRedirects(
            self.author_client.post(ADD_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        new_notes = Note.objects.exclude(slug__in=old_slugs)
        self.assertEqual(new_notes.count(), 1)
        new_note = new_notes.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Проверяет, что пользователь может редактировать свои заметки."""
        self.assertRedirects(
            self.author_client.post(EDIT_NOTE_URL, data=self.form_data),
            NOTE_SUCCESS_PAGE_URL
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_not_author_cant_edit_note(self):
        """Проверяет, пользователь не может редактировать чужие заметки."""
        self.assertEqual(
            self.reader_client.post(
                EDIT_NOTE_URL,
                data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Проверяет, что пользователь может удалять свои заметки."""
        initial_number_notes = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(DELETE_NOTE_URL),
            NOTE_SUCCESS_PAGE_URL
        )
        self.assertEqual(Note.objects.count(), initial_number_notes - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_not_author_cant_delete_note(self):
        """Проверяет, что пользователь не может удалять чужие заметки."""
        old_notes_id = list(Note.objects.values_list('id', flat=True))
        self.assertEqual(
            self.reader_client.delete(DELETE_NOTE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        notes = Note.objects.exclude(id__in=old_notes_id)
        self.assertEqual(notes.count(), 0)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
