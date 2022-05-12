from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title = 'Текстовая группа',
            description = 'Тестовое описание',
            slug = 'test-slug'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author = cls.user,
                text=f'Текст поста {i}',
                pub_date = 'Тестовая дата',
                group=cls.group,
            )
    
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contain_right_amount_of_records(self):
        amount_for_reverse = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 3
        }
        for reverse_name, amount in amount_for_reverse.items():
            response = self.authorized_client.get(reverse_name)
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(len(response.context['page_obj']), amount)
