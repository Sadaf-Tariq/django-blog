from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from .models import Post, Rating
from .forms import CommentForm, RatingForm
from django.contrib.auth.mixins import LoginRequiredMixin

# class (generic.ListView):
#     model = Post
#     queryset = Post.objects.filter(status=1).order_by("-created_on")
#     template_name = "index.html"
#     paginate_by = 6

class PostList(LoginRequiredMixin, generic.ListView):
    paginate_by = 6
    model = Post

    def get(self, request):
        posts = Post.objects.all().order_by('-created_on')
        for post in posts:
            rating = Rating.objects.filter(post=post).first()
            post.user_rating = rating.rating if rating else 0
        return render(self.request, "index.html", {"posts": posts})


def _get_form(request, formcls, prefix):
    data = request.POST if prefix in next(iter(request.POST.keys())) else None
    return formcls(data, prefix=prefix)

class PostDetail(View):

    commented = False

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

    

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": self.commented,
                "liked": liked,
                "comment_form": CommentForm(),
                "rating_form": RatingForm(),
            },
        )

    
    def post(self, request, slug, *args, **kwargs, ):


        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on") 
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        
        rating_form = RatingForm()
        comment_form = CommentForm()

        if 'rating_hidden_field' in self.request.POST:
            rating_form = RatingForm(data=request.POST)
            if rating_form.is_valid():
                counts = post.comments.filter(approved=False, name=request.user.username, post=post).count() 
                if counts > 0:
                    self.commented = True
                rating_form.instance.email = request.user.email
                rating_form.instance.user = request.user
                reviewCheck = Rating.objects.filter(user=request.user, post=post).count()
                if request.user.is_authenticated:
                    if reviewCheck > 0:
                        Rating.objects.filter(post=post, user=request.user).first().delete() 
                rating = rating_form.save(commit=False)
                rating.post = post
                rating.save()
                # return redirect('post_detail', post.slug)
            else:
                counts = post.comments.filter(approved=False, name=request.user.username, post=post).count() 
                if counts > 0:
                    self.commented = True

            

        if 'comment_hidden_field' in self.request.POST:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                self.commented = True
                comment_form.instance.email = request.user.email
                comment_form.instance.name = request.user.username
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.save()
                # return redirect('post_detail', post.slug)


        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": self.commented,
                "rating_form": rating_form,
                "comment_form": comment_form,
                "liked": liked,
            }
        )


class PostLike(View):

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))



def rate(request: HttpRequest, post_id: int, rating: int) -> HttpResponse:
    post = Post.objects.get(id=post_id)
    Rating.objects.filter(post=post).delete()
    post.rating_set.create(user=request.user, rating=rating)
    return index(request)
