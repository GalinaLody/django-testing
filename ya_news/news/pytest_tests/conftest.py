import pytest

from django.test.client import Client
from datetime import datetime, timedelta

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
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_11():
    today = datetime.today()
    all_11_news = [
        News(
            title=f'Новость {index}',
            text='Любой текст',
            date=today - timedelta(days=index)
        )
        for index in range(1, 12)
    ]
    News.objects.bulk_create(all_11_news)


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_comment_data():
    return {'text': 'Новый текст комментраия'}
