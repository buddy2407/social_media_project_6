from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from .models import Post,Comment,UserProfile
from django.views import View
from .forms import PostForm,CommentForm
from django.views.generic.edit import UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

# Create your views here.

class Postlist(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        posts=Post.objects.all().order_by('-created_on')
        form=PostForm()
        content = {
            'post_list':posts,
            'form':form
        }
        return render(request,'social_appe/post_list.html',content)

    def post(self,request,*args,**kwargs):
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST)
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.author=request.user
            new_post.save()
        content = {
            'post_list': posts,
            'form': form
        }
        return render(request, 'social_appe/post_list.html', content)
class PostDetailView(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        content={
            'post':post,
            'form':form,
            'comments': comments
        }
        return render(request,'social_appe/post_details.html',content)
    def post(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.post=post
            new_comment.author=request.user
            new_comment.save()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        content = {
            'post':post,
            'form':form,
            'comments':comments
        }
        return render(request,'social_appe/post_details.html',content)

class PostEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social_appe/post_edit.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social_appe/post_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social_appe/comment_delete.html'

    def get_success_url(self):
        pk=self.kwargs['post_pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class ProfileView(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        user=profile.user
        posts=Post.objects.filter(author=user).order_by('-created_on')

        followers=profile.followers.all()
        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers=len(followers)

        content={
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_followers':number_of_followers,
            'is_following':is_following
        }
        return render(request,'social_appe/profile.html',content)

class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','bio','birth_date','location','picture']
    template_name = 'social_appe/profile_edit_form.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('profile',kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        return redirect('profile',pk=profile.pk)

class RemoveFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile',pk=profile.pk)