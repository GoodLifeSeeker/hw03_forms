from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .models import Group, Post, User
from .forms import PostForm

NUMBER_OF_POSTS = 10


def index(request):
    template = 'posts/index.html'
    title = 'Последние записи'
    posts = Post.objects.all()
    keyword = request.GET.get('q', None)

    if keyword:
        posts = list((Post.objects.select_related('author', 'group')
                      .filter(text__contains=keyword)))
        if posts:
            title = 'Найдено:'
            posts = (Post.objects.select_related('author', 'group')
                     .filter(text__contains=keyword))
        else:
            title = 'По вашему запросу ничего не найдено.'

    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
        'keyword': keyword
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Записи сообщества '
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:NUMBER_OF_POSTS]
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'posts': posts,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    title = 'Профайл пользователя'
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_count = posts.count()
    context = {'title': title,
               'author': author,
               'posts_count': posts_count,
               'page_obj': page_obj,
               'posts': posts}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    context = {'post': post}
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    is_edit = False
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    else:
        context = {'form': form,
                   'is_edit': is_edit}
        return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        else:
            context = {'form': form,
                       'is_edit': is_edit}
            return render(request, template, context)
    else:
        if request.user.id == post.author.id:
            form = PostForm(instance=post)
            context = {'form': form,
                       'post': post,
                       'is_edit': is_edit}
            return render(request, template, context)
        else:
            return redirect('posts:post_detail', post_id)
