# Дима, извини за быдлокод, но... Получилось както-так
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа раз',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            pub_date='Тестовая дата',
            group=cls.group,
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа два',
            description='Тестовое описание группы',
            slug='test-slug2'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Проверяем, что шаблоны сформированы с правильным конекстом."""
        reverses = (
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                response_post = response.context.get('post')
                author = response_post.author
                group = response_post.group
                text = response_post.text
                pub_date = response_post.pub_date
                self.assertEqual(author, self.post.author)
                self.assertEqual(group, self.post.group)
                self.assertEqual(text, self.post.text)
                self.assertEqual(pub_date, self.post.pub_date)

    def test_post_create_and_edit_page_show_correct_context(self):
        """Проверяем, что шаблоны с формами сформированы с правильным
        контекстом."""
        reverses = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for reverse_name in reverses:
            response = self.authorized_client.get(reverse_name)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_exists_in_index_group_profile(self):
        """Проверяем, что созданный пост появился на главной странице,
        странице группы и на странице постов автора."""
        reverses_filters_dict = {
            reverse('posts:index'): Post.objects.all(),
            reverse('posts:group', kwargs={'slug': self.group.slug}):
                Post.objects.filter(group=self.post.group),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ): Post.objects.filter(author=self.post.author),
        }
        for reverse_name, filters in reverses_filters_dict.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTrue(filters.exists())

    def test_post_does_not_exist_in_another_group(self):
        """Проверяем, что созданный пост не появился в другой группе."""
        self.assertFalse(Post.objects.filter(group=self.group2).exists())
