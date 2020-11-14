from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View

from comment.forms import CommentForm
from comment.models import Comment
from .models import ArticlePost, ArticlePostForm, ArticleColumn

import markdown


# Create your views here.

def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')

    article_list = ArticlePost.objects.all()
    # 用户搜索
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # print(column)
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    for article in article_list:
        article.body = markdown.markdown(article.body,
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                # 目录扩展
                # 'markdown.extensions.toc',
            ])

    # 每页3篇文章
    paginator = Paginator(article_list, 3)
    # 获取url中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    context = {'articles': articles, 'order': order, 'search': search, 'coulum': column}
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = get_object_or_404(ArticlePost, id=id)

    comments = Comment.objects.filter(article=id).order_by('-created')

    article.total_views += 1
    # update_fields=[]指定了数据库只更新total_views字段，优化执行效率
    article.save(update_fields=['total_views'])

    # markdown语法渲染成html样式
    md = markdown.Markdown(
                                     extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite',
                                         # 目录扩展
                                         'markdown.extensions.toc',
                                     ])
    article.body = md.convert(article.body)

    comment_form = CommentForm()

    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form}
    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == 'POST':
        article_post_form = ArticlePostForm(request.POST, request.FILES)

        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])

            new_article.save()
            return redirect('article:article_list')
        else:
            return HttpResponse('表单内容有误，请重新填写')
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect('article:article_list')


@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method =='POST':
        article = ArticlePost.objects.get(id=id)

        if request.user != article.author:
            return HttpResponse('抱歉，你无权删除这篇文章')

        article.delete()
        return redirect('article:article_list')
    else:
        return HttpResponse('仅允许POST请求')


@login_required(login_url='/uesrprofile/login/')
def article_update(request, id):
    """
        更新文章的视图函数
        通过POST方法提交表单，更新titile、body字段
        GET方法进入初始表单页面
        id： 文章的 id
    """
    article = ArticlePost.objects.get(id=id)

    if request.user != article.author:
        return HttpResponse('抱歉，你无权修改这篇文章')

    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']

            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.save()
            return redirect('article:article_detail', id=id)
        else:
            return HttpResponse('表单内容有误，请重填')
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article': article, 'article_post_form': article_post_form, 'column': columns}
        return render(request, 'article/update.html', context)


class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')
