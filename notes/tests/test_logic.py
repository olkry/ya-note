from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from notes.models import Note


User = get_user_model()

FORM_NOTE = {
    'title': 'Тестовый заголовок 2',
    'text': 'Тестовый текст 2',
    'slug': 'test_2',
}


class TestNoteCreation(TestCase):
    global FORM_NOTE

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.add_url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = FORM_NOTE
        cls.login_url = reverse('users:login')

    def test_user_can_create_note(self):
        '''Авторизированный пользователь может создать запись'''
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        count = Note.objects.count()
        self.assertEqual(count, 1)
        note = Note.objects.get()
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])

    def test_anonymous_user_cant_create_comment(self):
        '''Аноним не может создать запись и редиректит на логин'''
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        expected_url = f'{self.login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        count = Note.objects.count()
        self.assertEqual(count, 0)


class TestLogicNode(TestCase):
    global FORM_NOTE
    TITLE = 'Тестовый заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text='Тестовый текст',
            slug='test',
            author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.form_data = FORM_NOTE
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_not_unique_slug(self):
        '''Не даст создать 2 слага'''
        self.form_data['slug'] = self.note.slug
        self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        '''Создание записи при пустой слаге'''
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.get(slug=expected_slug)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        '''Автор может редактировать свою заметку'''
        response = self.auth_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])

    def test_other_user_cant_edit_note(self):
        '''Не автор не может редактировать чужую заметку'''
        response = self.reader_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)

    def test_author_can_delete_note(self):
        '''Автор может удалить свою запись'''
        response = self.auth_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_reader_cant_delete_note(self):
        '''НЕ Автор может удалить свою запись'''
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
