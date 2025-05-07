from http import HTTPStatus
import pytest
import pdb

from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


from django.urls import reverse

from notes.models import Note


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:signup', 'users:logout')
)
def test_pages_availability_for_anonymous_user(client, name):
    # pdb.set_trace()
    url = reverse(name)
    response = client.get(url)
    if 'logout' in url:
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    else:
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


'''Тест БД и данных
def test_note_exists(note):
    notes_count = Note.objects.count()
    assert notes_count == 1
    assert note.title == 'Заголовок'


# Обращаемся к БД через декоратор
@pytest.mark.django_db
def test_empty_db():
    notes_count = Note.objects.count()
    assert notes_count == 0
'''


@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_author(author_client, name, note):
    url = reverse(name, args=(note.slug,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture(). НЕ РАБОТАЕТ!!!
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, note, expected_status
):
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    # Вторым параметром передаём note_object, 
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, args',
    (
        ('notes:detail', lf('slug_for_args')),
        ('notes:edit', lf('slug_for_args')),
        ('notes:delete', lf('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # # Формируем URL в зависимости от того, передан ли объект заметки:
    # if args is not None:
    #     url = reverse(name, args=(args.slug,))
    # else:
    #     url = reverse(name)
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
