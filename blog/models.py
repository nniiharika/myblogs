from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_blog = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_blogs')
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)  # Many-to-Many for likes


    def __str__(self):
        return self.title

    # Method to count likes
    def total_likes(self):
        return self.likes.count()
    
    def total_likes(self):
        return self.likes.count()

    # Check if the blog has child blogs
    def has_children(self):
        return self.child_blogs.exists()

    # Get all child blogs
    def get_children(self):
        return self.child_blogs.all()

class DailyBlog(Blog):
    # If you want to add specific fields to DailyBlog, you can do it here
    special_field = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"DailyBlog: {self.title}"

class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Ensure this field exists
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.blog.title}'
