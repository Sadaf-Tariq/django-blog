from django.shortcuts import render, get_object_or_404, reverse
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

    canAdd= True

    def get(self, request, slug, *args, **kwargs):
        # template_name = 'post_detail.html'
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        # canAdd= True
        reviewCheck = Rating.objects.filter(user=request.user, post=post).count()
        if request.user.is_authenticated:
            if reviewCheck > 0:
                self.canAdd= False

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "canAdd": self.canAdd,
                # "comment_form": CommentForm(),
                "aform": RatingForm(prefix='aform_pre'), 
                "bform": CommentForm(prefix='bform_pre'),
            },
        )
    

# class MyView(TemplateView):
#     template_name = 'mytemplate.html'

#     def get(self, request, *args, **kwargs):
#         return self.render_to_response({'aform': AForm(prefix='aform_pre'), 'bform': BForm(prefix='bform_pre')})

#     def post(self, request, *args, **kwargs):
#         aform = _get_form(request, AForm, 'aform_pre')
#         bform = _get_form(request, BForm, 'bform_pre')
#         if aform.is_bound and aform.is_valid():
#             # Process aform and render response
#         elif bform.is_bound and bform.is_valid():
#             # Process bform and render response
#         return self.render_to_response({'aform': aform, 'bform': bform})
    
    
    def post(self, request, slug, *args, **kwargs, ):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on") 

        # canAdd= True
        # reviewCheck = Rating.objects.filter(user=request.user, post=post).count()
        # if request.user.is_authenticated:
        #     if reviewCheck > 0:
        #         Rating.objects.filter(post=post, user=request.user).first().delete() 
                # self.canAdd= False
      

        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
    

        aform = _get_form(request, RatingForm, 'aform_pre')
        bform = _get_form(request, CommentForm, 'bform_pre')

        # if request.user.is_authenticated:
        #     Rating.objects.filter(post=post, user=request.user).first().delete()   

        if aform.is_bound and aform.is_valid():
            aform.instance.email = request.user.email
            aform.instance.user = request.user
            reviewCheck = Rating.objects.filter(user=request.user, post=post).count()
            if request.user.is_authenticated:
                if reviewCheck > 0:
                    Rating.objects.filter(post=post, user=request.user).first().delete() 
            rating = aform.save(commit=False)
            rating.post = post
            rating.save()
        elif bform.is_bound and bform.is_valid():
            bform.instance.email = request.user.email
            bform.instance.name = request.user.username
            comment = bform.save(commit=False)
            comment.post = post
            comment.save()

        # rating_form = RatingForm(data=request.POST)
        # if rating_form.is_valid():
        #     rating_form.instance.email = request.user.email
        #     rating_form.instance.user = request.user
        #     rating = rating_form.save(commit=False)
        #     rating.post = post
        #     rating.save()
        # else:
        #     rating_form = RatingForm()

        # comment_form = CommentForm(data=request.POST)
        # if comment_form.is_valid():
        #     comment_form.instance.email = request.user.email
        #     comment_form.instance.name = request.user.username
        #     comment = comment_form.save(commit=False)
        #     comment.post = post
        #     comment.save()
        # else:
        #     comment_form = CommentForm()

        

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                # "comment_form": comment_form,
                "canAdd": self.canAdd,
                # "rating_form": rating_form,
                "liked": liked,
                'aform': aform, 
                'bform': bform
            },
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
