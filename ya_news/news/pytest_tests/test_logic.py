import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_COMMENT_DATA = {'text': 'Другой комментарий'}


def test_user_can_create_comment(
    author_client,
    author,
    news,
    news_page_url
):
    """Авторизованный пользователь может отправить комментарий."""
    form_comment_data = FORM_COMMENT_DATA.copy()
    initial_number_comments = Comment.objects.count()
    assertRedirects(
        author_client.post(news_page_url, data=form_comment_data),
        f'{news_page_url}#comments'
    )
    assert Comment.objects.count() == initial_number_comments + 1
    comment_from_db = Comment.objects.get(
        text=form_comment_data['text'],
        news=news,
        author=author,
    )
    assert comment_from_db.text == form_comment_data['text']
    assert comment_from_db.author == author
    assert comment_from_db.news == news


def test_anonymous_user_cant_create_comment(
    client,
    news_page_url,
    user_login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    form_comment_data = FORM_COMMENT_DATA.copy()
    initial_number_comments = Comment.objects.count()
    assertRedirects(
        client.post(news_page_url, data=form_comment_data),
        f'{user_login_url}?next={news_page_url}'
    )
    assert Comment.objects.count() == initial_number_comments


def test_author_can_edit_comment(
    author_client,
    author,
    comment,
    news,
    comment_edit_url,
    news_page_url,
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    form_comment_data = FORM_COMMENT_DATA.copy()
    initial_number_comments = Comment.objects.count()
    assertRedirects(
        author_client.post(comment_edit_url, data=form_comment_data),
        news_page_url + '#comments'
    )
    assert Comment.objects.count() == initial_number_comments
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == form_comment_data['text']
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_not_author_cant_edit_comment(
        not_author_client,
        comment_edit_url,
        comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    form_comment_data = FORM_COMMENT_DATA.copy()
    initial_number_comments = Comment.objects.count()
    assert (
        not_author_client.post(
            comment_edit_url,
            data=form_comment_data
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert Comment.objects.count() == initial_number_comments
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(
        author_client,
        comment_delete_url,
        news_page_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    initial_number_comments = Comment.objects.count()
    assertRedirects(
        author_client.post(comment_delete_url),
        news_page_url + '#comments'
    )
    assert Comment.objects.count() == initial_number_comments - 1


def test_not_author_cant_delete_comment(
        not_author_client,
        comment_delete_url,
        comment
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    initial_number_comments = Comment.objects.count()
    assert (
        not_author_client.post(comment_delete_url).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert Comment.objects.count() == initial_number_comments
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(
        author_client, comment,
        comment_edit_url, bad_word
):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    form_comment_data = FORM_COMMENT_DATA.copy()
    initial_number_comments = Comment.objects.count()
    form_comment_data['text'] = f'Какой-то текст, {bad_word}, еще текст'
    assertFormError(
        author_client.post(
            comment_edit_url,
            data=form_comment_data
        ).context['form'],
        'text', errors=WARNING
    )
    assert initial_number_comments == Comment.objects.count()
