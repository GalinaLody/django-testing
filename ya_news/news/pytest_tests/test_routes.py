from http import HTTPStatus

from django.test.client import Client
import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


HOME_PAGE_URL = lazy_fixture('home_page_url')
NEWS_PAGE_URL = lazy_fixture('news_page_url')
USER_LOGIN_URL = lazy_fixture('user_login_url')
USER_SIGNUP_URL = lazy_fixture('user_signup_url')
USER_LOGOUT_URL = lazy_fixture('user_logout_url')
COMMENT_EDIT_URL = lazy_fixture('comment_edit_url')
COMMENT_DELETE_URL = lazy_fixture('comment_delete_url')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')
REDIRECT_NEWS_PAGE_TO_LOGIN_URL = lazy_fixture(
    'redirect_news_page_to_user_login_url'
)
REDIRECT_COMMENT_EDIT_PAGE_TO_LOGIN_URL = lazy_fixture(
    'redirect_comment_edit_page_to_login_url'
)
REDIRECT_COMMENT_DELETE_PAGE_TO_LOGIN_URL = lazy_fixture(
    'redirect_comment_delete_page_to_login_url'
)
client = Client()


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_PAGE_URL, client, HTTPStatus.OK),
        (NEWS_PAGE_URL, client, HTTPStatus.OK),
        (USER_LOGIN_URL, client, HTTPStatus.OK),
        (USER_SIGNUP_URL, client, HTTPStatus.OK),
        (USER_LOGOUT_URL, client, HTTPStatus.OK),
        (COMMENT_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (REDIRECT_COMMENT_EDIT_PAGE_TO_LOGIN_URL, client, HTTPStatus.OK),
        (REDIRECT_COMMENT_DELETE_PAGE_TO_LOGIN_URL, client, HTTPStatus.OK)
    )
)
def test_pages_availability_for_different_users_and_anonymous(
    parametrized_client, url, expected_status, user_logout_url
):
    """Проверяет доступность различных страниц сайта пользователям
    в зависимости от их статуса:
    анонимный пользователь, авторизованный пользователь, автор комментарий.
    """
    if url == user_logout_url:
        response = parametrized_client.post(url)
    else:
        response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_url',
    (
        (COMMENT_EDIT_URL, REDIRECT_COMMENT_EDIT_PAGE_TO_LOGIN_URL),
        (COMMENT_DELETE_URL, REDIRECT_COMMENT_DELETE_PAGE_TO_LOGIN_URL)
    )
)
def test_redirects(client, url, expected_url):
    """Анонимный пользователь, при попытке перейти на страницу
    удаления/редактирования комментариев перенаправляется
    на страницу авторизации.
    """
    assertRedirects(client.get(url), expected_url)
