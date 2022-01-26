from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from ..models import Group, Post, Comment, Follow
from django import forms
from django.core.cache import cache
import shutil
import tempfile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.groupwrong = Group.objects.create(
            title='Неправильная группа',
            slug='wrong-slug',
            description='Неправильное описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок, файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = Post.author

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # При обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        object = response.context['page_obj'][0]
        post_text = object.text
        post_image = object.image
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertIsNotNone(post_image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:group_posts", kwargs={"slug": self.group.slug})
        )
        object = response.context["page_obj"][0]
        post_text_0 = object.text
        post_group_0 = object.group
        post_image = object.image
        self.assertEqual(post_text_0, "Тестовый текст")
        self.assertEqual(post_group_0, self.group)
        self.assertIsNotNone(post_image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={'username': self.user})
        )
        object = response.context['page_obj'][0]
        post_text_0 = object.text
        post_group_0 = object.group
        post_author_0 = object.author
        post_image = object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.user)
        self.assertIsNotNone(post_image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        object = response.context['post']
        post_pk_0 = object.id
        post_image = object.image
        post_comments = Comment.objects.last()
        self.assertEqual(post_pk_0, self.post.pk)
        self.assertIsNotNone(post_image)
        self.assertEqual(post_comments, self.comment)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
        object = response.context['is_edit']
        self.assertTrue(object)

    def test_cache(self):
        """ Проверка работы кэширования главной страницы. """
        past_response = self.client.get(reverse('posts:index'))
        Post.objects.create(
            text='Кэшируемый текст, который удалится через 20 сек',
            author=self.user
        )
        future_response = self.client.get(reverse('posts:index'))
        self.assertEqual(past_response.content, future_response.content)

        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(past_response.content, response.content)

    def test_follow(self):
        self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )

    def test_unfollow(self):

        # сначала подписываем пользователя на author

        self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )

        # затем отписываем

        self.authorized_client.post(
            reverse('posts:profile_unfollow', kwargs={'username': self.user2})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.user2).exists()
        )

    def test_follow_feed(self):
        """Пост появояется в ленте подписчика"""
        self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )
        post = Post.objects.create(author=self.user2)
        response = self.authorized_client.post(
            reverse('posts:follow_index')
        )
        self.assertIn(post, response.context['page_obj'])

    def test_unfollow_feed(self):
        """Пост не появояется в ленте неподписчика"""

        # сначала подписываем пользователя на author

        self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.user2})
        )

        # затем отписываем

        self.authorized_client.post(
            reverse('posts:profile_unfollow', kwargs={'username': self.user2})
        )
        post = Post.objects.create(author=self.user2)
        response = self.authorized_client.post(
            reverse('posts:follow_index')
        )
        self.assertNotIn(post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.page_obj.append(
                Post(
                    author=cls.user,
                    text='Тестовый текст' + str(i),
                    group=cls.group,
                )
            )

        cls.pages = Post.objects.bulk_create(cls.page_obj)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        # Проверка: на первой странице должно быть десять постов.
        list = [
            (reverse('posts:index')),
            (reverse('posts:group_posts', kwargs={'slug': self.group.slug})),
            (reverse('posts:profile', kwargs={'username': self.user}))
        ]
        for reverse_name in list:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        list = [
            (reverse('posts:index') + '?page=2'),
            (reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ) + '?page=2'),
            (reverse(
                'posts:profile', kwargs={'username': self.user}
            ) + '?page=2')
        ]
        for reverse_name in list:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 3)
