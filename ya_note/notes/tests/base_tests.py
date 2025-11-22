from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

NOTE_SLUG = ('slug',)

ADD_NOTE_URL = reverse('notes:add')
DELETE_NOTE_URL = reverse('notes:delete', args=NOTE_SLUG)
DETAIL_NOTE_PAGE_URL = reverse('notes:detail', args=NOTE_SLUG)
EDIT_NOTE_URL = reverse('notes:edit', args=NOTE_SLUG)
HOME_PAGE_URL = reverse('notes:home')
NOTE_LIST_URL = reverse('notes:list')
NOTE_SUCCESS_PAGE_URL = reverse('notes:success')
USER_LOGIN_URL = reverse('users:login')
USER_SIGNUP_URL = reverse('users:signup')
USER_LOGOUT_URL = reverse('users:logout')


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
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.user = User.objects.create(
            username='Любой залогиненный пользователь'
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
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
