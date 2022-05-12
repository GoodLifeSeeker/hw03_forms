from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title = 'Текстовый заголовок',
            description = 'Тестовое описание группы',
            slug = 'test-slug'
        )
        cls.post = Post.objects.create(
            author = cls.user,
            text='Тестовый текст',
            pub_date = 'Тестовая дата',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    
    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_users_page(self):
        """Тестируем доступность страниц неавторизованными пользователями."""
        urls_http_status_dict = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, expected_value in urls_http_status_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, expected_value)

    def test_authorized_users_page(self):
        """Тестируем доступность страниц авторизованными пользователями."""
        # Остальное протестировали в test_guest_users_page
        urls_http_status_dict = {
            '/create/': HTTPStatus.OK,
        }
        # Позже однотипных тестов может быть больше, поэтому subTest
        for address, expected_value in urls_http_status_dict.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, expected_value)

    def test_author_page(self):
        """Тестируем доступность страниц автором."""
        # Остальное протестировали выше
        urls_http_status_dict = {
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
        }
        # Позже однотипных тестов может быть больше, поэтому subTest
        for address, expected_value in urls_http_status_dict.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, expected_value)
    
    def test_redirect_guest_users(self):
        """Тестируем редирект неавторизованных пользователей."""
        url_redirectedurl_dict = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': 
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
        }
        for address, expected_redirect in url_redirectedurl_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, expected_redirect)
