from django.shortcuts import reverse
from django.test import TestCase, Client

from posts.models import Group, Post, User

SLUG = 'test-slug'
USERNAME = 'post_author'
NOT_AUTHOR_USERNAME = 'not_post_author'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_posts', args=[SLUG])
PROFILE_URL = reverse('profile', args=[USERNAME])
FOLLOW_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[USERNAME])
LOGIN_URL = f'{reverse("login")}?next='
ERROR_404_URL = '4e567tgt8hu9/'


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username=USERNAME)
        cls.user_not_author = User.objects.create(username=NOT_AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug=SLUG,
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user_author,
            group=cls.group
        )
        cls.POST_URL = reverse('post', args=[
            USERNAME, cls.post.id])
        cls.POST_EDIT_URL = reverse('post_edit', args=[
            USERNAME, cls.post.id])
        cls.COMMENT_URL = reverse('add_comment', args=[
            USERNAME, cls.post.id])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(cls.user_not_author)
        cls.authorized_author.force_login(cls.user_author)

    def test_urls_available_for_any_client(self):
        """Страницы доступны пользователям с соответствующими правами."""
        guest = self.guest_client
        author = self.authorized_author
        not_author = self.authorized_client
        url_client_status_code_values = [
            [INDEX_URL, guest, 200],
            [GROUP_URL, guest, 200],
            [PROFILE_URL, guest, 200],
            [NEW_POST_URL, author, 200],
            [NEW_POST_URL, guest, 302],
            [FOLLOW_URL, guest, 302],
            [FOLLOW_URL, not_author, 200],
            [PROFILE_FOLLOW_URL, guest, 302],
            [PROFILE_FOLLOW_URL, not_author, 302],
            [PROFILE_FOLLOW_URL, author, 302],
            [PROFILE_UNFOLLOW_URL, guest, 302],
            [PROFILE_UNFOLLOW_URL, not_author, 302],
            [self.COMMENT_URL, guest, 302],
            [self.COMMENT_URL, not_author, 302],
            [self.COMMENT_URL, author, 302],
            [self.POST_URL, guest, 200],
            [self.POST_EDIT_URL, author, 200],
            [self.POST_EDIT_URL, guest, 302],
            [self.POST_EDIT_URL, not_author, 302],
            [ERROR_404_URL, guest, 404]
        ]
        for url, client, status_code in url_client_status_code_values:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).status_code, status_code
                )

    def test_urls_redirect_user_on_correct_page(self):
        """Страницы перенаправляют пользователей
        на соответствующие страницы.
        """
        guest = self.guest_client
        not_author = self.authorized_client
        author = self.authorized_author
        redirects_client_urls_values = [
            [NEW_POST_URL, guest, LOGIN_URL + NEW_POST_URL],
            [PROFILE_FOLLOW_URL, guest, LOGIN_URL + PROFILE_FOLLOW_URL],
            [PROFILE_FOLLOW_URL, not_author, PROFILE_URL],
            [PROFILE_FOLLOW_URL, author, PROFILE_URL],
            [PROFILE_UNFOLLOW_URL, guest, LOGIN_URL + PROFILE_UNFOLLOW_URL],
            [PROFILE_UNFOLLOW_URL, not_author, PROFILE_URL],
            [self.POST_EDIT_URL, not_author, self.POST_URL],
            [self.POST_EDIT_URL, guest, LOGIN_URL + self.POST_EDIT_URL],
            [self.COMMENT_URL, guest, LOGIN_URL + self.COMMENT_URL],
        ]
        for url, client, redirect in redirects_client_urls_values:
            with self.subTest(url=url):
                self.assertRedirects(
                    client.get(url, follow=True), redirect
                )

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_urls_names = [
            [INDEX_URL, 'index.html'],
            [GROUP_URL, 'group.html'],
            [PROFILE_URL, 'profile.html'],
            [NEW_POST_URL, 'new.html'],
            [FOLLOW_URL, 'follow.html'],
            [self.POST_URL, 'post.html'],
            [self.POST_EDIT_URL, 'new.html'],
        ]
        for url, template in templates_urls_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_author.get(url),
                    template)
