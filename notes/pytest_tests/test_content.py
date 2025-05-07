import pytest


from django.urls import reverse
from pytest_lazy_fixtures import lf

from notes.forms import NoteForm


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (lf('author_client'), True),
        (lf('not_author_client'), False),
    )
)
def test_notes_list_for_different_users(
        note, parametrized_client, note_in_list
):
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


''' Проверка форм
def test_create_note_page_contains_form(author_client):
    url = reverse('notes:add')
    # Запрашиваем страницу создания заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)


# В параметры теста передаём фикстуру slug_for_args и клиент с автором заметки:
def test_edit_note_page_contains_form(slug_for_args, author_client):
    url = reverse('notes:edit', args=slug_for_args)
    # Запрашиваем страницу редактирования заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm) 
'''


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', lf('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)



