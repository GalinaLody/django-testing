from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_COMMENT_DATA = {'text': 'Другой комментарий'}
FORM_COMMENT_BED_WORDS = [{'text': bad_word} for bad_word in BAD_WORDS]


def test_user_can_create_comment(
    author_client,
    author,
    news,
    news_page_url,
    news_page_with_comment_url
):
    """Авторизованный пользователь может отправить комментарий."""
    assertRedirects(
        author_client.post(news_page_url, data=FORM_COMMENT_DATA),
        news_page_with_comment_url
    )
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get()
    assert comment_from_db.text == FORM_COMMENT_DATA['text']
    assert comment_from_db.author == author
    assert comment_from_db.news == news


def test_anonymous_user_cant_create_comment(
    client,
    news_page_url,
    redirect_news_page_to_user_login_url,
):
    """Анонимный пользователь не может отправить комментарий."""
    assertRedirects(
        client.post(news_page_url, data=FORM_COMMENT_DATA),
        redirect_news_page_to_user_login_url
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client,
    author,
    comment,
    news,
    comment_edit_url,
    news_page_with_comment_url,
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    assertRedirects(
        author_client.post(comment_edit_url, data=FORM_COMMENT_DATA),
        news_page_with_comment_url
    )
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == FORM_COMMENT_DATA['text']
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_not_author_cant_edit_comment(
        not_author_client,
        comment_edit_url,
        comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    assert (
        not_author_client.post(
            comment_edit_url,
            data=FORM_COMMENT_DATA
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(
        author_client,
        comment_delete_url,
        news_page_with_comment_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    assertRedirects(
        author_client.post(comment_delete_url),
        news_page_with_comment_url
    )
    assert Comment.objects.count() == 0


def test_not_author_cant_delete_comment(
        not_author_client,
        comment_delete_url,
        comment
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    assert (
        not_author_client.post(comment_delete_url).status_code
        == HTTPStatus.NOT_FOUND
    )
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


@pytest.mark.parametrize('form_comment_bed_words', FORM_COMMENT_BED_WORDS)
def test_user_cant_use_bad_words(
        author_client,
        news_page_url, form_comment_bed_words
):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    assertFormError(
        author_client.post(
            news_page_url,
            data=form_comment_bed_words
        ).context['form'],
        'text', errors=WARNING
    )
    assert Comment.objects.count() == 0
