from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.tests.base_tests import (
    CommonBaseTest,
    ADD_NOTE_URL,
    DETAIL_NOTE_PAGE_URL,
    DELETE_NOTE_URL,
    EDIT_NOTE_URL,
    HOME_PAGE_URL,
    NOTE_SUCCESS_PAGE_URL,
    NOTE_LIST_URL,
    USER_LOGIN_URL,
    USER_LOGOUT_URL,
    USER_SIGNUP_URL
)

User = get_user_model()


class TestRoutes(CommonBaseTest):
    """Тесты маршрутов приложения заметок."""

    def test_pages_availability(self):
        """Проверка доступа пользователей
        с различным статусам к страницам сайта.
        """
        users_statuses = [
            [
                self.author_client,
                DETAIL_NOTE_PAGE_URL,
                HTTPStatus.OK
            ],
            [
                self.author_client,
                EDIT_NOTE_URL,
                HTTPStatus.OK
            ],
            [
                self.author_client,
                DELETE_NOTE_URL,
                HTTPStatus.OK
            ],
            [
                self.not_author_client,
                DETAIL_NOTE_PAGE_URL,
                HTTPStatus.NOT_FOUND
            ],
            [
                self.not_author_client,
                EDIT_NOTE_URL,
                HTTPStatus.NOT_FOUND
            ],
            [
                self.not_author_client,
                DELETE_NOTE_URL,
                HTTPStatus.NOT_FOUND
            ],
            [
                self.not_author_client,
                NOTE_LIST_URL,
                HTTPStatus.OK
            ],
            [
                self.not_author_client,
                ADD_NOTE_URL,
                HTTPStatus.OK
            ],
            [
                self.not_author_client,
                NOTE_SUCCESS_PAGE_URL,
                HTTPStatus.OK
            ],
            [
                self.client,
                HOME_PAGE_URL,
                HTTPStatus.OK
            ],
            [
                self.client,
                USER_LOGIN_URL,
                HTTPStatus.OK
            ],
            [
                self.client,
                USER_SIGNUP_URL,
                HTTPStatus.OK
            ],
            [
                self.client,
                USER_LOGOUT_URL,
                HTTPStatus.OK
            ]
        ]
        for user, url, status in users_statuses:
            with self.subTest(user=user, url=url, status=status):
                if url == USER_LOGOUT_URL:
                    self.assertEqual(user.post(url).status_code, status)
                else:
                    self.assertEqual(user.get(url).status_code, status)

    def test_redirect_for_anonymous_user(self):
        """Проверка редиректа анонимного пользователя со страниц
        списка заметок, успешного добавлния заметки,
        страницы отдельной заметки,
        редактирования и удаления заметки.
        """
        urls = (
            DETAIL_NOTE_PAGE_URL,
            NOTE_SUCCESS_PAGE_URL,
            ADD_NOTE_URL,
            NOTE_LIST_URL,
            EDIT_NOTE_URL,
            DELETE_NOTE_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    f'{USER_LOGIN_URL}?next={url}'
                )
