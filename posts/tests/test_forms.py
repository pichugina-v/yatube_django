import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase, override_settings
from django import forms

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SLUG = 'test-slug'
NEW_SLUG = 'new-test-slug'
USERNAME = 'test_name'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
TEST_IMAGE = (b'\x47\x49\x46\x38\x39\x61\x01\x00'
              b'\x01\x00\x00\x00\x00\x21\xf9\x04'
              b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
              b'\x00\x00\x01\x00\x01\x00\x00\x02'
              b'\x02\x4c\x01\x00\x3b')
IMAGE_NAME = 'image.gif'
IMAGE_TYPE = 'image/gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Текст первого поста',
            author=cls.user,
            group=cls.group
        )
        cls.image = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=TEST_IMAGE,
            content_type=IMAGE_TYPE
        )
        cls.POST_URL = reverse('post', args=[
            USERNAME, cls.post.id])
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            USERNAME, cls.post.id])
        cls.COMMENT_URL = reverse('add_comment', args=[
            USERNAME, cls.post.id])
        cls.Form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        existing_posts_id = tuple(
            Post.objects.all().values_list('id', flat=True)
        )
        form_data = {
            'text': 'Текст второго поста',
            'group': self.group.id,
            'image': self.image
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        new_query_objects = Post.objects.all().exclude(
            id__in=existing_posts_id
        )
        self.assertEqual(
            new_query_objects.count(), 1
        )
        new_post = new_query_objects.last()
        self.assertEqual(
            new_post.text,
            form_data['text']
        )
        self.assertEqual(
            new_post.group.id,
            form_data['group']
        )
        self.assertIn(
            os.path.relpath(new_post.image.name, start='posts'),
            os.listdir(os.path.join(settings.MEDIA_ROOT, 'posts'))
        )
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1
        )

    def test_edit_existing_post(self):
        """Валидная форма редактирует запись в Post."""
        new_group = Group.objects.create(
            title='Тестовое название новой группы',
            slug=NEW_SLUG
        )
        form_data = {
            'text': 'Отредактированный текст первого поста',
            'group': new_group.id
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        updated_post = response.context['post']
        self.assertEqual(
            updated_post.id,
            self.post.id
        )
        self.assertEqual(
            updated_post.text,
            form_data['text']
        )
        self.assertEqual(
            updated_post.group.id,
            form_data['group']
        )
        self.assertRedirects(response, self.POST_URL)

    def test_authorized_user_can_add_comment(self):
        """Авторизированный пользователь может
        комментировать посты.
        """
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True)
        self.assertEqual(
            Comment.objects.count(), 1
        )
        new_comment = response.context['page'][0]
        self.assertEqual(
            new_comment.text,
            form_data['text']
        )

    def test_new_post_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        urls = [NEW_POST_URL, self.POST_EDIT_URL]
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_comments_shows_correct_context(self):
        """Шаблон comments сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.COMMENT_URL)
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField)