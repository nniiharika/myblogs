from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import create_pdf, view_blog



urlpatterns = [
    path('', views.index, name='index'),  
    path('home/', views.home, name='home'),
    path('create/', views.create_blog, name='create_blog'),
    path('blog/<int:blog_id>/', views.view_blog, name='view_blog'),
    path('edit/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('delete/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('blog/<int:blog_id>/like/', views.like_blog, name='like_blog'),
    path('blog/<int:blog_id>/add_comment/', views.add_comment, name='add_comment'),
    path('create_pdf/<int:blog_id>/', create_pdf, name='create_pdf'), 
    path('<int:blog_id>/', view_blog, name='view_blog'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
