from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

SLUG = 'test-slug'
USERNAME = 'test_name'
AUTHOR_USERNAME = 'author_name'


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный идентификатор',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text(self):
        """help_text в полях модели Group совпадает с ожидаемым"""
        field_help_texts = {
            'title': 'Придумайте название группы',
            'slug': ('Укажите идентификатор для страницы задачи. '
                     'Используйте только латиницу, '
                     'цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).help_text,
                    expected
                )

    def test_object_name_is_title_field(self):
        """В поле __str__  объекта group записан group.title."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(
            expected_object_name,
            str(group)
        )


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(title='test_group')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым"""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым"""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': ('Вы можете выбрать группу, '
                      'в которой хотите опубликовать пост')
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text,
                    expected
                )

    def test_object_names_are_correct_fields(self):
        """В поле __str__  объекта post записаны
        post.author.username, post.pub_date,
        первые 15 символов post.text, post.group
        """
        post = self.post
        pub_date = post.pub_date
        expected_objects_names = (f'{post.author.username}, '
                                  f'{pub_date}, '
                                  f'{post.text[:15]}, '
                                  f'{post.group}')
        self.assertEqual(
            expected_objects_names,
            str(post)
        )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария'
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        field_verboses = {
            'post': 'Пост',
            'author': 'Комментарий к посту',
            'text': 'Текст комментария',
            'created': 'Дата публикации комменатрия'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Comment._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text(self):
        """help_text модели Comment совпадает с ожидаемым"""
        self.assertEqual(
            Comment._meta.get_field('text').help_text,
            'Введите Ваш комментарий'
        )

    def test_object_names_are_correct_fields(self):
        """В поле __str__  объекта comment записаны
        comment.author.username, comment.created,
        первые 15 символов comment.text, comment.group
        """
        comment = self.comment
        created = comment.created
        expected_objects_names = (f'{comment.author.username}, '
                                  f'{created}, '
                                  f'{comment.text[:15]}, '
                                  f'{comment.post}')
        self.assertEqual(
            expected_objects_names,
            str(comment)
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.author_user = User.objects.create(username=AUTHOR_USERNAME)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author_user
        )

    def test_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Follow._meta.get_field(value).verbose_name,
                    expected
                )

    def test_object_names_are_correct_fields(self):
        """В поле __str__  объекта comment записаны
        comment.author.username, comment.created,
        первые 15 символов comment.text, comment.group
        """
        follow = self.follow
        expected_objects_names = (f'Подписчик: {follow.user.username}, '
                                  f'автор: {follow.author.username}')
        self.assertEqual(
            expected_objects_names,
            str(follow)
        )
