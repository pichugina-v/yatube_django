import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase, override_settings

from posts.models import Comment, Follow, Group, Post, User
from posts.settings import POSTS_PER_PAGE_NUMBER

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SLUG = 'test-slug'
NOT_POST_GROUP_SLUG = 'wrong-group-slug'
USERNAME = 'test_name'
AUTHOR_USERNAME = 'author_name'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
POST_GROUP_URL = reverse('group_posts', args=[SLUG])
NOT_POST_GROUP_URL = reverse('group_posts', args=[NOT_POST_GROUP_SLUG])
FOLLOW_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[AUTHOR_USERNAME])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[AUTHOR_USERNAME])
PROFILE_URL = reverse('profile', args=[AUTHOR_USERNAME])
TEST_IMAGE = (b'\x47\x49\x46\x38\x39\x61\x01\x00'
              b'\x01\x00\x00\x00\x00\x21\xf9\x04'
              b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
              b'\x00\x00\x01\x00\x01\x00\x00\x02'
              b'\x02\x4c\x01\x00\x3b')
IMAGE_NAME = 'test_image.gif'
IMAGE_TYPE = 'image/gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.user_author = User.objects.create(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=TEST_IMAGE,
            content_type=IMAGE_TYPE
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user_author,
            group=cls.group,
            image=cls.image
        )
        cls.comment = Comment.objects.create(
            text='Текст комментария',
            post=cls.post,
            author=cls.user
        )
        cls.POST_URL = reverse('post', args=[
            AUTHOR_USERNAME, cls.post.id])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_on_pages_show_correct_context(self):
        """Страницы с постами сформированы с правильным контекстом."""
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        urls = [INDEX_URL, POST_GROUP_URL, PROFILE_URL,
                self.POST_URL, FOLLOW_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if 'post' in response.context:
                    post = response.context['post']
                else:
                    self.assertEqual(len(response.context['page']), 1)
                    post = response.context['page'][0]
                self.assertEqual(
                    post.text,
                    self.post.text
                )
                self.assertEqual(
                    post.author,
                    self.post.author
                )
                self.assertEqual(
                    post.group,
                    self.post.group
                )
                self.assertEqual(
                    post.image.name,
                    self.post.image.name
                )

    def test_profile_post_pages_show_correct_context(self):
        """Шаблоны личных страниц отображают
        соответствующую информацию об авторах.
        """
        url_names = [PROFILE_URL, self.POST_URL]
        for url in url_names:
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).context['author'],
                    self.post.author
                )

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(POST_GROUP_URL)
        group = response.context['group']
        self.assertEqual(
            group.title,
            self.group.title
        )
        self.assertEqual(
            group.description,
            self.group.description
        )
        self.assertEqual(
            group.slug,
            self.group.slug
        )

    def test_comments_show_correct_context(self):
        """Страница post с комметариями
        сформирована с правильным контекстом.
        """
        response = self.authorized_client.get(self.POST_URL)
        self.assertEqual(len(response.context['page']), 1)
        comment = response.context['page'][0]
        self.assertEqual(
            comment.text,
            self.comment.text
        )
        self.assertEqual(
            comment.author,
            self.comment.author
        )
        self.assertEqual(
            comment.post,
            self.comment.post
        )

    def test_post_with_group_not_appear_at_wrong_group_page(self):
        """Пост с указанием группы не отображается
        на странице группы, не указанной автором поста.
        """
        Group.objects.create(
            title='Группа без поста',
            slug=NOT_POST_GROUP_SLUG,
        )
        response = self.guest_client.get(NOT_POST_GROUP_URL)
        self.assertNotIn(
            self.post,
            response.context['page']
        )

    def test_post_with_group_not_appear_at_wrong_follower_page(self):
        """"Новая запись пользователя не появляется в ленте тех,
        кто не подписан на него.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )
        response = self.authorized_client.get(FOLLOW_URL)
        self.assertNotIn(
            self.post,
            response.context['page']
        )

    def test_authorized_user_can_follow_author(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )

    def test_authorized_user_can_unfollow_author(self):
        """Авторизованный пользователь может удалять
        из подписок других пользователей.
        """
        Follow.objects.create(
            user=self.user,
            author=self.post.author
        )
        self.authorized_client.get(PROFILE_UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user.id,
                author=self.post.author.id
            ).exists()
        )

    def test_index_page_is_cached(self):
        """Cписок постов на странице index хранится в кэше."""
        response = self.authorized_client.get(INDEX_URL)
        Post.objects.create(
            text='Текст, который отобразится через 20 сек',
            author=self.user
        )
        cached_response = self.authorized_client.get(INDEX_URL)
        self.assertEqual(
            response.content,
            cached_response.content
        )
        cache.clear()
        not_cached_response = self.authorized_client.get(INDEX_URL)
        self.assertNotEqual(
            response.content,
            not_cached_response.content
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        for post in range(POSTS_PER_PAGE_NUMBER + 3):
            Post.objects.create(
                text='Тестовый текст поста',
                author=cls.user)

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_expected_number_of_records(self):
        """Количество постов на первой странице index
        соотвествует ожидаемому.
        """
        self.assertEqual(
            len(self.client.get(INDEX_URL).context['page']),
            POSTS_PER_PAGE_NUMBER
        )

    def test_second_page_contains_three_records(self):
        """Количество постов на второй странице index
        соотвествует ожидаемому.
        """
        self.assertEqual(
            len(self.client.get(INDEX_URL + '?page=2').context['page']), 3
        )
