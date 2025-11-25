from datetime import datetime, timedelta
import time

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_for_all(db):
    ...


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )


@pytest.fixture
def news_list_on_home_page():
    News.objects.bulk_create(News(
        title=f'Новость {index}',
        text='Любой текст',
        date=datetime.today() - timedelta(days=index)
    )for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comments_list(news, author):
    for index in range(settings.COMMENTS_COUNT_ON_PAGE + 1):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария{index}'
        )
        time.sleep(1)


@pytest.fixture
def home_page_url():
    return reverse('news:home')


@pytest.fixture
def news_page_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_page_with_comment_url(news_page_url):
    return f'{news_page_url}#comments'


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def user_login_url():
    return reverse('users:login')


@pytest.fixture
def user_signup_url():
    return reverse('users:signup')


@pytest.fixture
def user_logout_url():
    return reverse('users:logout')


@pytest.fixture
def redirect_news_page_to_user_login_url(news_page_url, user_login_url):
    return f'{user_login_url}?next={news_page_url}'


@pytest.fixture
def redirect_comment_edit_page_to_login_url(comment_edit_url, user_login_url):
    return f'{user_login_url}?next={comment_edit_url}'


@pytest.fixture
def redirect_comment_delete_page_to_login_url(
    comment_delete_url,
    user_login_url
):
    return f'{user_login_url}?next={comment_delete_url}'
