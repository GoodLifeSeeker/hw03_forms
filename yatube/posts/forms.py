from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ('Пост'),
            'group': ('группа:'),
        }
        help_texts = {
            'text': ('Тут пишите буквы'),
            'group': ('Выберите из доступных:'),
        }