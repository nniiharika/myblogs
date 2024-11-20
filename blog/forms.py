from django import forms
from .models import Blog, Comment

class BlogForm(forms.ModelForm):
    parent_blog = forms.ModelChoiceField(
        queryset=Blog.objects.filter(parent_blog__isnull=True),
        required=False,
        label="Parent Blog",
        help_text="Select a parent blog if this is a child blog."
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'parent_blog']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
