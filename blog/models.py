from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db.models import Avg

STATUS = ((0, 'Draft'), (1, 'Published'))


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    featured_image = CloudinaryField('image', default='placeholder')
    excerpt = models.TextField(blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    likes = models.ManyToManyField(
        User, related_name='blogpost_like', blank=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()

    def average_rating(self) -> float:
        return Rating.objects.filter(post_id=self).aggregate(Avg("rating"))["rating__avg"] or 0

def field_validation(value):
    """
    Function to validate servings,estimated_time and calorie_count field values
    """
    if value == 0:
        raise ValidationError(
            ('The value should be greater than zero'),
            params={'value': value},
        )

class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    name = models.CharField(max_length=50)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment {self.body} by {self.name}"



class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    email = models.EmailField()
    rating = models.PositiveIntegerField(blank=False, default=0,
        validators=[field_validation, MaxValueValidator(5)]) #validator addition

    def __str__(self):
        return f"{self.post.title}: {self.rating}"

