from django.test import TestCase
from django.shortcuts import reverse

from posts.models import Post, User

SLUG = 'test-slug'
USERNAME = 'test_name'


class RoutesTest(TestCase):
    def test_routes_correspond_url_names(self):
        """Прямые маршруты соответствуют рассчетам по URL name."""
        self.user = User.objects.create(username=USERNAME)
        post = Post.objects.create(text='test_text', author=self.user)
        routes_reverse_names = [
            ['/', reverse('index')],
            ['/new/', reverse('new_post')],
            ['/follow/', reverse('follow_index')],
            [f'/group/{SLUG}/', reverse('group_posts', args=[
                SLUG])],
            [f'/{USERNAME}/follow/', reverse('profile_follow', args=[
                USERNAME])],
            [f'/{USERNAME}/unfollow/', reverse('profile_unfollow', args=[
                USERNAME])],
            [f'/{USERNAME}/', reverse('profile', args=[
                USERNAME])],
            [f'/{USERNAME}/{post.id}/', reverse('post', args=[
                USERNAME, post.id])],
            [f'/{USERNAME}/{post.id}/edit/', reverse('post_edit', args=[
                USERNAME, post.id])],
            [f'/{USERNAME}/{post.id}/comment/', reverse('add_comment', args=[
                USERNAME, post.id])],
        ]
        for route, name in routes_reverse_names:
            self.assertEqual(route, name)
