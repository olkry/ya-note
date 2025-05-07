from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Test Author')
        cls.notes = Note.objects.create(
            title='Тестовый заголовок 1',
            text='Тестовый текст 1',
            slug='test_1',
            author=cls.author
        )
        cls.user = User.objects.create(username='Test User')

    def test_nologin_page_availability(self):
        '''Набор доступности страниц для незалогиненого пользователя'''
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None)

        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if 'logout' in url:
                    self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_and_delete(self):
        '''Доступ стороннего пользователя к записям автора'''
        users_statuses = (
            (self.user, HTTPStatus.NOT_FOUND),
            (self.author, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        '''Редирект анонима на страницу логина'''
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:detail', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                print(redirect_url, '|||', response, end='\n')
                self.assertRedirects(response, redirect_url)
