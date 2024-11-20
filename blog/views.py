from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BlogForm, CommentForm
from django.contrib import messages
from django.http import FileResponse
from django.http import HttpResponse, HttpResponseNotFound
from .models import Blog, Comment 
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.conf import settings
from reportlab.lib.utils import ImageReader
from django.conf import settings
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO
from . import views
import os

def index(request):
    return render(request, 'blog/index.html')

def home(request):
    # Retrieve only parent blogs (blogs that don't have a parent_blog)
    blogs = Blog.objects.filter(parent_blog__isnull=True)
    return render(request, 'blog/home.html', {'blogs': blogs})

def search(request):
    query = request.GET.get('q')
    results = Blog.objects.filter(title__icontains=query)  # Filter blogs by title
    return render(request, 'blog/search_results.html', {'results': results, 'query': query})

def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('home')
    else:
        form = BlogForm()
    return render(request, 'blog/create_blog.html', {'form': form})

def view_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comments = blog.comments.all()
    
    # Check if the blog is a parent blog
    if blog.parent_blog is None:
        child_blogs = blog.get_children()  # or however you get the children blogs
    else:
        child_blogs = None
    
    comment_form = CommentForm()
    pdf_url = request.build_absolute_uri(f'/blog/{blog_id}/generate_pdf/')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.author = request.user
            new_comment.save()
            return redirect('view_blog', blog_id=blog.id)
    
    return render(request, 'blog/view_blog.html', {
        'blog': blog,
        'comments': comments,
        'child_blogs': child_blogs,
        'comment_form': comment_form,
    })

def create_pdf(request, blog_id):
    # Fetch the blog content based on blog_id
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return HttpResponse("Blog not found", status=404)

    # Create a BytesIO object to store the PDF
    buffer = BytesIO()

    # Create a PDF with ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add the blog title at the top of the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Blog Title: {blog.title}")

    # Handle long content text by wrapping it
    p.setFont("Helvetica", 12)
    text_object = p.beginText(100, 720)
    text_object.setFont("Helvetica", 12)

    content_lines = blog.content.split("\n")
    for line in content_lines:
        wrapped_lines = wrap_text(line, 90)  # Wrap the text within the given width
        for wrapped_line in wrapped_lines:
            text_object.textLine(wrapped_line)

    p.drawText(text_object)

    # Adjust the Y position to leave space between text and the image
    current_y = text_object.getY()  # Get the current Y position after the text

    # Image handling: Check if the blog has an image and place it below the text
    if blog.image:
        image_path = os.path.join(settings.MEDIA_ROOT, str(blog.image))
        if os.path.exists(image_path):
            try:
                # Ensure the image is placed below the text without overlapping
                image = ImageReader(image_path)
                image_width = 4 * inch
                image_height = 3 * inch

                # Check if there's enough space for the image; if not, add a new page
                if current_y - image_height < 0:
                    p.showPage()  # Create a new page if there isn't enough space
                    current_y = 750  # Reset Y position on the new page

                # Draw the image
                p.drawImage(image, 100, current_y - image_height - 20, width=image_width, height=image_height)
            except Exception as e:
                print(f"Error adding image: {e}")

    p.showPage()
    p.save()

    # Move to the beginning of the BytesIO buffer
    buffer.seek(0)

    # Serve the PDF as an HTTP response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="blog_{blog_id}.pdf"'

    return response

def wrap_text(text, width):
    """A helper function to wrap text lines to fit within the page width."""
    from textwrap import wrap
    return wrap(text, width=width)


def view_pdf(request, blog_id):
    """View the PDF of the blog."""
    # Retrieve the blog object
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return HttpResponseNotFound("Blog not found.")
    
    # Create the PDF if it doesn't exist
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, f'blog_{blog.id}.pdf')
    if not os.path.exists(pdf_file_path):
        create_pdf(blog)

    # Serve the PDF file
    if os.path.exists(pdf_file_path):
        return FileResponse(open(pdf_file_path, 'rb'), content_type='application/pdf')
    else:
        return HttpResponseNotFound("PDF file not found.")


def like_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)  # Unlike the blog
    else:
        blog.likes.add(request.user)  # Like the blog
    return redirect('view_blog', blog_id=blog.id)  # Correctly use blog_id

def add_comment(request, blog_id):
    # Retrieve the blog using the blog_id
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # Save the comment but don't commit to the database just yet
            comment = comment_form.save(commit=False)
            comment.blog = blog  # Assign the blog to the comment
            comment.author = request.user  # Set the author to the logged-in user
            comment.save()  # Now save the comment
            return redirect('view_blog', blog_id=blog.id)  # Redirect back to the blog view
    else:
        comment_form = CommentForm()

    # Render the template and pass the blog and comment form
    return render(request, 'blog/view_blog.html', {
        'blog': blog,
        'comment_form': comment_form,
    })
    
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Only the author can edit their own blog
    if request.user != blog.author:
        messages.error(request, "You are not authorized to edit this blog.")
        return redirect('view_blog', blog_id=blog.id)  # Redirect back to the blog view

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Your blog has been successfully updated!")
            return redirect('view_blog', blog_id=blog.id)  # Redirect to the updated blog post
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blog/edit_blog.html', {'form': form, 'blog': blog})


def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    print(f"Blog ID: {blog.id}")  # Print the blog ID
    print(f"Request User: {request.user}")  # Print the logged-in user

    # Only the author can delete their own blog
    if request.user != blog.author:
        messages.error(request, "You are not authorized to delete this blog.")
        return redirect('view_blog', blog_id=blog.id)

    if request.method == 'POST':
        blog.delete()
        messages.success(request, "Your blog has been successfully deleted.")
        return redirect('home')  # Redirect to home after deletion

    return render(request, 'blog/delete_blog.html', {'blog': blog})
