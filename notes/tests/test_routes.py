from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Гога или Жора')
        cls.reader = User.objects.create(username='Анон нереальный')
        cls.notes = Note.objects.create(title='Название заметки',
                                        text='Текст заметки',
                                        author=cls.author)

    def test_page_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
            ('notes:delete', (self.notes.slug,)),
            ('notes:list', None),
            ('notes:success', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if name == 'notes:add' or name == 'notes:list' or name == 'notes:success':
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                elif args is None:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_availability_for_accessing_notes(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),

        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in (
                    'notes:edit',
                    'notes:delete',
                    'notes:detail',
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.notes.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anon(self):
        login_url = reverse('users:login')
        for name in (
                'notes:edit',
                'notes:delete',
                'notes:detail',
        ):
            with self.subTest(name=name):
                url = reverse(name, kwargs={'slug': self.notes.slug})
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
