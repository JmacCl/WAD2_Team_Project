from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from eruditoapp.models import Subject, Thread, Comment, User,  Vote, ThreadVote, UserProfile, UsefulResource, ThreadReport, CommentReport
from eruditoapp.forms import SubjectForm, ThreadForm, UserForm, UserProfileForm, CommentForm, EditProfileForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.forms import PasswordChangeForm
# Create your views here.


def about(request):
    context_dict= {}
    return render(request, 'erudito/about.html', context=context_dict)

def home(request):
    context_dict= {}
    subject_list= Subject.objects.all()
    context_dict['subjects']= subject_list
    return render(request, 'erudito/home.html', context=context_dict)

def subjects(request):
    context_dict= {}
    subject_list= Subject.objects.all()
    context_dict['subjects']= subject_list
    return render(request, 'erudito/subjects.html', context= context_dict)


def show_subject(request, subject_name_slug, sort='-score'):
    context_dict={}
    try:
        subject= Subject.objects.get(slug=subject_name_slug)
        threads= Thread.objects.filter(subject=subject).order_by(sort)

        if request.user.is_authenticated:
            votes_map=[]
            for thread in threads:
                if ThreadVote.objects.filter(thread=thread, user=request.user, like_type="like").exists():
                    votes_map.append("liked") #indicates thread has already been liked, this will change the display of the button on the html.
                elif ThreadVote.objects.filter(thread=thread, user=request.user, like_type="dislike").exists():
                    votes_map.append("disliked")  #indicates thread has already been disliked, this will change the display of the button on the html.
                else: 
                    votes_map.append("nolike")  #indicates thread has not been liked, this will change the display of the button on the html.
            thread_votes= zip(threads, votes_map)
            context_dict['votes']= thread_votes
        context_dict['threads']= threads
        context_dict['subject']= subject

    except Subject.DoesNotExist:
        context_dict['threads']= None
        context_dict['subject']= None
    return render(request, 'erudito/subject.html', context=context_dict)

def show_thread(request, subject_name_slug, thread_name_slug):
    context_dict={}
    try:
        subject= Subject.objects.get(slug=subject_name_slug)
        thread= Thread.objects.get(slug=thread_name_slug)
        comments= Comment.objects.filter(thread=thread).order_by('-score')
        if request.user.is_authenticated:
            votes_map= []
            for comment in comments:
                if Vote.objects.filter(comment=comment, user=request.user, like_type= "like").exists():
                    votes_map.append("liked") #indicates comment has already been liked, this will change the display of the button on the html.
                elif Vote.objects.filter(comment=comment, user=request.user, like_type= "dislike").exists():
                    votes_map.append("disliked") #indicates comment has already been "disliked", this will change the display of the button on the html.
                else:
                    votes_map.append("nolike") #indicates comment has not been liked/disliked. 
                    
            comment_votes= zip(comments, votes_map) #associates liked/disliked values with corresponding comment       
            context_dict['votes'] = comment_votes
        context_dict['subject']= subject
        context_dict['thread']= thread
        context_dict['comments']= comments

    except Thread.DoesNotExist:
        context_dict['thread']= None
        context_dict['comments']= None
    return render(request, 'erudito/thread.html', context= context_dict)

@login_required
def add_thread(request, subject_name_slug):
    try:
        subject= Subject.objects.get(slug=subject_name_slug)
    except Subject.DoesNotExist:
        subject= None
    try:
        user= request.user
    except User.DoesNotExist:
        user= None

    if subject is None:
        return redirect('/')
    if user is None:
        return redirect('/')

    form= ThreadForm()
    if request.method=="POST":
        form= ThreadForm(request.POST)
        if form.is_valid():
            if subject:
                thread= form.save(commit=False)
                thread.subject = subject
                thread.score= 0
                thread.user= user
                thread.save()
                return redirect(reverse('eruditoapp:show_subject', kwargs={'subject_name_slug':
                                                                       subject_name_slug}))

            else:
                print(form.errors)
    context_dict= {'form':form, 'subject': subject}
    return render(request, 'erudito/add_thread.html', context=context_dict)

def add_comment(request, subject_name_slug, thread_name_slug):
    try:
        thread= Thread.objects.get(slug=thread_name_slug)
        subject= Subject.objects.get(slug=subject_name_slug)
    except Thread.DoesNotExist:
        thread= None
    except Subject.DoesNotExist:
        subject= None
    try:
        user= request.user
    except User.DoesNotExist:
        user= None

    if thread is None:
        return redirect('/')
    if user is None:
        return redirect('/')
    form= CommentForm()
    if request.method=="POST":
        form= CommentForm(request.POST)
        if form.is_valid():
                if thread:
                    comment= form.save(commit=False)
                    comment.thread= thread
                    comment.score= 0
                    comment.user= user
                    comment.save()
                    return redirect(reverse('eruditoapp:show_thread', kwargs={'subject_name_slug':
                                                                           subject_name_slug, 'thread_name_slug':
                                                                           thread_name_slug}))

                else:
                    print(form.errors)

    context_dict= {'form':form, 'subject': subject, 'thread': thread}
    return render(request, 'erudito/add_comment.html', context=context_dict)

def register(request):
    registered= False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form= UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user= user

            if 'picture' in request.FILES:
                profile.picture= request.FILES['picture']
            else:
                profile.picture= 'Default.jpg'
            profile.save()
            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form= UserProfileForm()

    return render(request, 'erudito/register.html', context= {'user_form': user_form,
                                                            'profile_form': profile_form,
                                                            'registered': registered})

def user_login(request):
    context_dict={}
    if request.method == 'POST':
        username= request.POST.get('username')
        password= request.POST.get('password')
        user= authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('eruditoapp:about'))
            else:
                context_dict['message']="Your account is disabled."
                return render(request, 'erudito/login.html',context=context_dict)
        else:
            context_dict['message']="invalid login details supplied."
            return render(request, 'erudito/login.html',context=context_dict)
    else:
        return render(request, 'erudito/login.html')

def useful_resources(request,subject_name_slug):
    context_dict ={}
    subject = Subject.objects.get(slug=subject_name_slug)
    context_dict['subject'] = subject
    useful_resources = UsefulResource.objects.filter(subject = subject)
    context_dict['resources'] = useful_resources



    return render(request, 'erudito/useful-resources.html', context=context_dict)


class LikeCommentView(View):
    @method_decorator(login_required)
    def get(self, request):
        comment_id = request.GET['comment_id']
        like_type= request.GET['like_type']
        try:
            comment = Comment.objects.get(id=int(comment_id))
        except Comment.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        user= comment.user #user here refers to comment author, not request/logged in/current active user
        try:
            userprof= UserProfile.objects.get(user=user)     
        except UserProfile.DoesNotExist:
            userprof=None
        if like_type=="like":
            comment.score = comment.score + 1
            vote = Vote(user=request.user, like_type='like')
            userprof.score= userprof.score + 1
            try:
                old_vote= Vote.objects.filter(user= request.user, comment=comment, like_type="dislike")
                old_vote.delete() #replaces the old dislike vote for the new like vote, affecting the html display, i.e. whether a like or dislike button is shown
            except Vote.DoesNotExist:
                pass

        elif like_type=="dislike":
            comment.score = comment.score - 1
            vote = Vote(user=request.user, like_type='dislike')            
            userprof.score= userprof.score - 1
            try:
                old_vote= Vote.objects.filter(user= request.user, comment=comment, like_type="like")
                old_vote.delete() #replaces the old like vote for the new dislike vote, affecting the html display, i.e. whether a like or dislike button is shown
            except Vote.DoesNotExist:
                pass


        comment.save()
        vote.save()    
        userprof.save()
        vote.comment.add(comment)

        return HttpResponse(comment.score)

class LikeThreadView(View):
    @method_decorator(login_required)
    def get(self, request):
        thread_id = request.GET['thread_id']
        like_type= request.GET['like_type']
        try:
            thread = Thread.objects.get(id=int(thread_id))
        except Thread.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        user= thread.user #user here refers to comment author, not request/logged in/current active user
        try:
            userprof= UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            userprof=None
            
        if like_type=="like":
            thread.score= thread.score +1
            vote = ThreadVote(user= request.user, like_type='like')
            userprof.score= userprof.score +1
            try:
                old_vote= ThreadVote.objects.filter(user= request.user, thread=thread, like_type="dislike")
                old_vote.delete() #replaces the old dislike vote for the new like vote, affecting the html display, i.e. whether a like or dislike button is shown
            except ThreadVote.DoesNotExist:
                pass
        elif like_type=="dislike":
            thread.score= thread.score -1
            vote = ThreadVote(user= request.user, like_type='dislike')
            userprof.score= userprof.score -1
            try:
                old_vote= ThreadVote.objects.filter(user= request.user, thread=thread, like_type="like")
                old_vote.delete() #replaces the old like vote for the new like vote, affecting the html display, i.e. whether a like or dislike button is shown
            except ThreadVote.DoesNotExist:
                pass
            
        vote.save()
        thread.save()
        vote.thread.add(thread)
        userprof.save()


        return HttpResponse(thread.score)
    

    

@login_required
def my_account(request):
    context_dict={}
    threads= Thread.objects.filter(user=request.user)
    context_dict['threads']= threads
    return render(request, 'erudito/my_account.html', context=context_dict)


def show_user(request, user_name_slug):
    context_dict={}
    try:
        user = User.objects.get(username=user_name_slug)
        context_dict['ouser']= user
        threads= Thread.objects.filter(user=user)
        context_dict['threads']= threads
    except Subject.DoesNotExist:
        context_dict['ouser']= None
        context_dict['threads'] = None
    return render(request, 'erudito/profile.html', context=context_dict)

@login_required
def restricted(request):
    return render(request, 'erudito/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('eruditoapp:about'))

def edit_profile(request):
    if request.method =='POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('eruditoapp:my_account')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request,'erudito/edit_profile.html', args)

def search_thread(request, subject_name_slug, sort='-score'):

    context_dict={}
    if(request.method == 'GET'):
        thread_title = request.GET.get('search')
        try:
            subject= Subject.objects.get(slug=subject_name_slug)
            threads= Thread.objects.filter(title__icontains = thread_title, subject =subject).order_by(sort)
            
            #reusing liking logic from show_subject view
            if request.user.is_authenticated:
                votes_map=[]
                for thread in threads:
                    if ThreadVote.objects.filter(thread=thread, user=request.user, like_type="like").exists():
                        votes_map.append("liked")
                    elif ThreadVote.objects.filter(thread=thread, user=request.user, like_type="dislike").exists():
                        votes_map.append("disliked")
                    else: 
                        votes_map.append("nolike")

                thread_votes= zip(threads, votes_map)
                context_dict['votes']= thread_votes
            context_dict['threads']= threads
            context_dict['subject']= subject
        except Subject.DoesNotExist or Thread.DoesNotExist:
            context_dict['threads']= None
            context_dict['subject']= None
        return render(request,'erudito/subject.html',context=context_dict)
    else:
        return render(request,'erudito/subject.html',context=context_dict)

def report_problem(request, subject_name_slug, thread_name_slug, comment_id=None):

        
    context_dict={}
    try: 
        thread= Thread.objects.get(slug=thread_name_slug)
        subject= Subject.objects.get(slug=subject_name_slug)
        if comment_id:
            comment= Comment.objects.get(id=comment_id)
    except Thread.DoesNotExist or Subject.DoesNotExist or Comment.DoesNotExist:
        context_dict['thread']= None
        context_dict['subject']= None
        context_dict['comment']= None
    context_dict['thread']= thread
    context_dict['subject']= subject
    if comment_id:
        context_dict['comment']= comment

    if request.method=="POST":
        body= request.POST.get("report_body")
        if comment_id:
            report= CommentReport(user=request.user, body=body)
            report.save()
            report.comment.add(comment)
        else:
            report= ThreadReport(user=request.user, body=body)
            report.save()
            report.thread.add(thread)
        return redirect(reverse('eruditoapp:home'))

    return render(request,'erudito/report.html', context=context_dict)