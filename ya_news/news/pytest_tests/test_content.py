import pytest

from django.urls import reverse
from pytest_lazyfixture import lazy_fixture


@pytest.mark.usefixtures('news_11')
def test_not_more_ten_news_on_home_page(client):
    """Проверяет, что на главной странице
    отображается не более 10 страниц.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == 10


@pytest.mark.usefixtures('news_11')
def test_news_order(client):
    """Проверяет, что посты отсортированны по датам в порядке убывания."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def comments_order(news, news_id_for_args, not_author_client):
    """Проверяет, что комментарии на странице отсортированы
    в порядке возрастания.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = not_author_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_comments_dates = [comment.created for comment in all_comments]
    sorted_comments_dates = sorted(all_comments_dates)
    assert all_comments_dates == sorted_comments_dates


@pytest.mark.usefixtures('news')
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (lazy_fixture('not_author_client'), True),
        (lazy_fixture('client'), False),
    )
)
def test_add_comment_for_different_users(
    parametrized_client,
    form_in_context,
    news_id_for_args
):
    """Проверяет, что форма для отправки комментов доступна
    только авторизованному пользователю и не доступна анонимному.
    """
    url = reverse('news:detail', args=news_id_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
