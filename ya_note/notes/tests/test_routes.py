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
    USER_SIGNUP_URL,
    REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL,
    REDIRECT_DETAIL_NOTE_TO_USER_LOGIN_URL,
    REDIRECT_NOTE_SUCCESS_PAGE_TO_USER_LOGIN_URL,
    REDIRECT_NOTE_LIST_TO_USER_LOGIN_URL,
    REDIRECT_EDIT_NOTE_TO_USER_LOGIN_URL,
    REDIRECT_DELETE_NOTE_TO_USER_LOGIN_URL,
    OK, NOT_FOUND

)

User = get_user_model()


class TestRoutes(CommonBaseTest):
    """Тесты маршрутов приложения заметок."""

    def test_pages_availability(self):
        """Проверка доступа пользователей
        с различным статусам к страницам сайта.
        """
        users_statuses = [
            [self.author_client, DETAIL_NOTE_PAGE_URL, OK],
            [self.author_client, EDIT_NOTE_URL, OK],
            [self.author_client, DELETE_NOTE_URL, OK],
            [self.reader_client, DETAIL_NOTE_PAGE_URL, NOT_FOUND],
            [self.reader_client, EDIT_NOTE_URL, NOT_FOUND],
            [self.reader_client, DELETE_NOTE_URL, NOT_FOUND],
            [self.reader_client, NOTE_LIST_URL, OK],
            [self.reader_client, ADD_NOTE_URL, OK],
            [self.reader_client, NOTE_SUCCESS_PAGE_URL, OK],
            [self.client, HOME_PAGE_URL, OK],
            [self.client, USER_LOGIN_URL, OK],
            [self.client, USER_SIGNUP_URL, OK],
            [self.client, USER_LOGOUT_URL, OK],
            [self.client, REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL, OK],
            [self.client, REDIRECT_DETAIL_NOTE_TO_USER_LOGIN_URL, OK],
            [self.client, REDIRECT_NOTE_SUCCESS_PAGE_TO_USER_LOGIN_URL, OK],
            [self.client, REDIRECT_NOTE_LIST_TO_USER_LOGIN_URL, OK],
            [self.client, REDIRECT_EDIT_NOTE_TO_USER_LOGIN_URL, OK],
            [self.client, REDIRECT_DELETE_NOTE_TO_USER_LOGIN_URL, OK]
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
            (DETAIL_NOTE_PAGE_URL, REDIRECT_DETAIL_NOTE_TO_USER_LOGIN_URL),
            (
                NOTE_SUCCESS_PAGE_URL,
                REDIRECT_NOTE_SUCCESS_PAGE_TO_USER_LOGIN_URL
            ),
            (ADD_NOTE_URL, REDIRECT_ADD_NOTE_TO_USER_LOGIN_URL),
            (NOTE_LIST_URL, REDIRECT_NOTE_LIST_TO_USER_LOGIN_URL),
            (EDIT_NOTE_URL, REDIRECT_EDIT_NOTE_TO_USER_LOGIN_URL),
            (DELETE_NOTE_URL, REDIRECT_DELETE_NOTE_TO_USER_LOGIN_URL)
        )
        for url, expected_url in urls:
            with self.subTest(url=url, expected_url=expected_url):
                self.assertRedirects(
                    self.client.get(url),
                    expected_url
                )
