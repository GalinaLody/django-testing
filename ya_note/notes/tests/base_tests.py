from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

NOTE_SLUG = 'slug'

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND

ADD_NOTE_URL = reverse('notes:add')
DELETE_NOTE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
DETAIL_NOTE_PAGE_URL = reverse('notes:detail', args=(NOTE_SLUG,))
EDIT_NOTE_URL = reverse('notes:edit', args=(NOTE_SLUG,))
HOME_PAGE_URL = reverse('notes:home')
NOTE_LIST_URL = reverse('notes:list')
NOTE_SUCCESS_PAGE_URL = reverse('notes:success')
USER_LOGIN_URL = reverse('users:login')
USER_SIGNUP_URL = reverse('users:signup')
USER_LOGOUT_URL = reverse('users:logout')
REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL = f'{USER_LOGIN_URL}?next={ADD_NOTE_URL}'
REDIRECT_DETAIL_NOTE_TO_USER_LOGIN_URL = (
    f'{USER_LOGIN_URL}?next={DETAIL_NOTE_PAGE_URL}'
)
REDIRECT_NOTE_SUCCESS_PAGE_TO_USER_LOGIN_URL = (
    f'{USER_LOGIN_URL}?next={NOTE_SUCCESS_PAGE_URL}'
)
REDIRECT_NOTE_LIST_TO_USER_LOGIN_URL = f'{USER_LOGIN_URL}?next={NOTE_LIST_URL}'
REDIRECT_EDIT_NOTE_TO_USER_LOGIN_URL = f'{USER_LOGIN_URL}?next={EDIT_NOTE_URL}'
REDIRECT_DELETE_NOTE_TO_USER_LOGIN_URL = (
    f'{USER_LOGIN_URL}?next={DELETE_NOTE_URL}'
)


class CommonBaseTest(TestCase):
    """Общий базовый класс для тестов.

    Создаёт пользователей,
    авторизует клиентов для каждого из них и создаёт тестовую заметку.
    Также подготавливает словарь с данными формы
    для создания/редактирования заметки.
    Класс предназначен для наследования,
    чтобы переиспользовать общие тестовые данные.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель-не автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст заметки',
            'slug': 'new_slug'
        }
