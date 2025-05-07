from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotePage(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author,
        )
        cls.not_author = User.objects.create(username='Не автор')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')

    def test_availability_notes_different_users(self):
        '''Доступность записей разным пользователям'''
        users_statuses = (
            (self.not_author, False),
            (self.author, True),
        )
        for user, found in users_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            answer = self.note in object_list
            self.assertEqual(answer, found)

    def test_authorized_client_has_form(self):
        '''Доступность форм на добовлении и редактировании иеё соответствие'''
        self.client.force_login(self.author)
        for url in (self.add_url, self.edit_url):
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
