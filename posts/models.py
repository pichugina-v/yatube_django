from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Придумайте название группы'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный идентификатор',
        help_text=('Укажите идентификатор для страницы задачи. '
                   'Используйте только латиницу, '
                   'цифры, дефисы и знаки подчёркивания')
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text=('Вы можете выбрать группу, '
                   'в которой хотите опубликовать пост')
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text=('Вы можете добавить изображение, '
                   'к Вашему посту')
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return (f'{self.author.username}, '
                f'{self.pub_date}, '
                f'{self.text[:15]}, '
                f'{self.group}')


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к посту'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите Ваш комментарий'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комменатрия'
    )

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'{self.author.username}, '
                f'{self.created}, '
                f'{self.text[:15]}, '
                f'{self.post}')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'Подписчик: {self.user.username}, '
                f'автор: {self.author.username}')
