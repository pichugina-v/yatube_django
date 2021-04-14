from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import POSTS_PER_PAGE_NUMBER


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and request.user != author
        and Follow.objects.filter(
            author=author, user=request.user
        ).exists()
    )
    return render(request, 'profile.html', {
        'page': page,
        'author': author,
        'following': following
    })


def post_view(request, username, post_id):
    form = CommentForm()
    post = get_object_or_404(Post,
                             id=post_id,
                             author__username=username)
    following = (
        request.user.is_authenticated
        and request.user != post.author
        and Follow.objects.filter(
            author=post.author, user=request.user
        ).exists()
    )
    comment_list = post.comments.all()
    paginator = Paginator(comment_list, POSTS_PER_PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'form': form,
        'page': page,
        'comments': comment_list,
        'following': following,
    })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
    return redirect('post',
                    username,
                    post_id)


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form
        })
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post',
                        username,
                        post_id)
    post = get_object_or_404(Post,
                             id=post_id,
                             author__username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form,
            'post': post
        })
    form.save()
    return redirect('post',
                    username,
                    post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {
        'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not (
        request.user.username == username or author.following.filter(
            user=request.user
        ).exists()
    ):
        Follow.objects.create(author=author, user=request.user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow,
                      user=request.user,
                      author__username=username).delete()
    return redirect('profile',
                    username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request,
                  'misc/404.html',
                  {'path': request.path},
                  status=404)


def server_error(request):
    return render(request,
                  'misc/500.html',
                  status=500)
