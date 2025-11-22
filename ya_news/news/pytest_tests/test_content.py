from django.conf import settings

from news.forms import CommentForm


def test_not_more_ten_news_on_home_page(
        client,
        home_page_url,
        news_list_on_home_page
):
    """Проверяет, что на главной странице отображается не более 10 страниц."""
    assert (
        client.get(home_page_url).context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(
        client,
        home_page_url,
        news_list_on_home_page
):
    """Проверяет, что посты отсортированны по датам в порядке убывания."""
    all_dates = [
        news.date
        for news in client.get(home_page_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(
        news,
        not_author_client,
        news_page_url,
        comments_list
):
    """Проверяет, что комментарии на странице отсортированы
    в порядке возрастания.
    """
    all_comments = (
        not_author_client
        .get(news_page_url)
        .context['news']
        .comment_set.all()
    )
    all_comments_dates = [comment.created for comment in all_comments]
    assert (
        [comment.created for comment in all_comments]
        == sorted(all_comments_dates)
    )


def test_add_comment_for_authorized_user(
    not_author_client,
    news_page_url,
    news
):
    """Проверяет, что форма для отправки комментов доступна
    только авторизованному пользователю.
    """
    assert 'form' in not_author_client.get(news_page_url).context
    assert isinstance(
        not_author_client.get(news_page_url).context['form'],
        CommentForm
    )


def test_not_add_comment_for_anonymous(
    news_page_url,
    news,
    client
):
    """Проверяет, что форма для отправки комментов не доступна анонимному."""
    assert 'form' not in client.get(news_page_url).context
