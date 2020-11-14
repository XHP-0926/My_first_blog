from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django import forms

from PIL import Image

# Create your models here.

class ArticleColumn(models.Model):
    # 栏目model
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now())
    updated = models.DateTimeField(auto_now=True)
    total_views = models.PositiveIntegerField(default=0)
    column = models.ForeignKey(ArticleColumn, on_delete=models.CASCADE, null=True, blank=True, related_name='article')
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        article = super(ArticlePost, self).save(*args, **kwargs)

        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        return article

    # 获取文章地址
    def get_absolute_url(self):
        print(reverse('article:article_detail', args=[self.id]))
        return reverse('article:article_detail', args=[self.id])

    # bug
    def was_created_recently(self):
        diff = timezone.now() - self.created
        if diff.days == 0 and diff.seconds >=0 and diff.seconds < 60:
            return True
        else:
            return False

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body', 'avatar')





