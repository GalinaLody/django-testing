from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(
    author_client,
    author,
    form_comment_data,
    news_id_for_args
):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_comment_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_comment_data['text']
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(
    client,
    form_comment_data,
    news_id_for_args
):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=news_id_for_args)
    client.post(url, form_comment_data)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(
        author_client, comment,
        comment_id_for_args,
        form_comment_data
):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    url = reverse('news:edit', args=comment_id_for_args)
    form_comment_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(url, data=form_comment_data)
    comment.refresh_from_db()
    assertFormError(response.context['form'], 'text', errors=WARNING)


def test_author_can_edit_comment(
    author_client,
    form_comment_data,
    comment,
    comment_id_for_args,
    news_id_for_args
):
    """Авторизованный пользователь может редактировать."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_comment_data)
    assertRedirects(response, reverse(
        'news:detail',
        args=news_id_for_args
    ) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_comment_data['text']


def test_other_user_cant_edit_comment(
        not_author_client,
        form_comment_data,
        comment_id_for_args,
        comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=form_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
        author_client,
        comment_id_for_args,
        news_id_for_args
):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse(
        'news:detail',
        args=news_id_for_args
    ) + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
        not_author_client,
        comment_id_for_args
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
