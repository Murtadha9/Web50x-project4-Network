from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator   
import json 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt   
from .models import *  



def index(request):

    if request.user.is_authenticated:
        return render(request, "network/index.html")
    else:
        return HttpResponseRedirect(reverse("login"))
    

#####################################################################
@login_required 
def post(request):
    if request.method == "POST":
        form_contents = request.POST["Textarea"]
        newpost = Post(author=request.user, postText=form_contents)
        newpost.save()
        return HttpResponseRedirect(reverse("allPosts"))
    else:
        return render(request, "network/post.html")


#####################################################################
@login_required
def allPosts(request):
    posts = Post.objects.all().order_by('-posted')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/allPosts.html", {
        "page_obj": page_obj
    })


#####################################################################
@login_required
def profile(request, user_id):
    profile = User.objects.get(id=user_id)
    if Follow.objects.filter(user=user_id, followed_by=request.user).exists():
        following_status = True
    else:
        following_status = False
    followList = []
    following = request.user.following.all()
    for x in following:
        followList.append(x.user.id)
    posts = Post.objects.filter(author=user_id).order_by('-posted')
  
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "page_obj": page_obj,
        "viewed_profile": profile.username,
        "viewed_profile_id": user_id,
        "posts": posts,
        "following": profile.following.all().count(),
        "followedBy": Follow.objects.filter(user=user_id).count(),
        "following_status": following_status
    })

#####################################################################

@login_required
def following(request):
    usersFollowed = request.user.following.all()
    usersFollowedIds = []
    for x in usersFollowed:
        usersFollowedIds.append(x.user.id)
    posts = Post.objects.filter(author__in=usersFollowedIds).order_by('-posted')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


#####################################################################
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


# Log user out
@login_required(redirect_field_name='my_redirect_field')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Register a new user
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


#####################################################################
@login_required
def follow(request, user_id):
    user = User.objects.get(pk=request.user.id)
    print("Debug:", user, type(user), user.following.all())
    profile = User.objects.get(pk=user_id)
    print("Debug:", profile, type(profile), profile.following.all())
    if Follow.objects.filter(user=profile, followed_by=user).exists():        
        instance = Follow.objects.filter(user=profile, followed_by=user).get()
        user.following.remove(instance)
        a = Follow.objects.filter(user=profile)
        for x in a:
            if not x.followed_by.exists():
                x.delete()
    else:
        instance = Follow(user=profile)
        instance.save()
        instance.followed_by.add(user)
    return JsonResponse({"message": "Profile successfully followed / unfollowed"}, status=201)


#####################################################################
@csrf_exempt
@login_required
def edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    data = json.loads(request.body)
    new_text = data.get("post", "t")
    post.postText = new_text
    post.save()
    return JsonResponse({"message": "Post successfully edited", "new_text": new_text}, status=201)

#####################################################################
@csrf_exempt
@login_required
def like(request, post_id):
    user = User.objects.get(id=request.user.id)
    post = Post.objects.get(id=post_id)
    if user in post.like.all():
        post.like.remove(user)
    else:
        post.like.add(user)
    return JsonResponse({"message": "Post successfully liked / disliked"})