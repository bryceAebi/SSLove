from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as AuthUser
from django.core.urlresolvers import reverse
from django.contrib.auth.views import logout, login as login_view
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from users.models import ApprovedEmail


def change_password(request):
    template_response = views.password_change(request)
    return template_response

def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/sendlove/')
    else:
        return login_view(request)

def custom_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/') 

def homepage(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/sendlove/')
    else:
        return HttpResponseRedirect('/login/')

def signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    if request.method == 'GET':
        return render(request, 'users/signup.html')
    elif request.method == 'POST':
        # Check they filled in the form correctly
        if not (request.POST.get('password', '') and request.POST.get('email', '')):
            return render(
                request,
                'users/signup.html',
                {'errors': ['Missing password or email']},
            )

        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        # Check that their email is approved
        approved_emails = ApprovedEmail.objects.filter(email=email.lower())[:1]
        if approved_emails:
            approved_email = approved_emails[0]
        else:
            return render(
                request,
                'users/signup.html',
                {
                    'errors': [
                        'Unidentified email. Make sure you enter your StyleSeat email. \
                        If you did and are still experiencing this error, contact Bryce to \
                        add your email to the approved email list.'
                    ]
                },
            )
        
        # Check for pre-existing account
        if AuthUser.objects.filter(email=email):
            return render(
                request,
                'users/signup.html',
                {'errors': ['Pre-existing account. You should log in instead.']},
            )

        # At this point, they have passed authentication
        name = approved_email.name
        name_chunks = name.split(" ")
        user = AuthUser.objects.create_user(
            approved_email.email,  # we're using the email as username, too
            email=approved_email.email,
            password=password,
            first_name=name_chunks[0],
            last_name=name_chunks[1],
        )

        approved_email.user = user
        approved_email.save()

        # Login
        new_user = authenticate(
            username=request.POST['email'],
            password=request.POST['password'],
        )
        login(request, new_user)

        return HttpResponseRedirect('/sendlove/')


def profile(request, fullname=None):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))
    if fullname:
        name = fullname.replace('_', ' ')
        users = ApprovedEmail.objects.filter(name=name)
        if not users:
            raise Http404('User does not exist')
        user = users[0]
    else:
        user = ApprovedEmail.objects.get(id=request.user.approvedemail.id)
    sent_loves = user.sent_love.order_by('-id')
    sent_love_count = sent_loves.count()
    recieved_loves = user.recieved_love.order_by('-id')
    recieved_love_count = recieved_loves.count()
    if recieved_love_count == 0:
        love_ratio = 'n/a'
    else:
        love_ratio =  str((1.0 * sent_love_count / recieved_love_count))[:4]
        
    return render(
        request,
        'users/profile.html', 
        {
            'sent_loves': sent_loves[:35],
            'recieved_loves': recieved_loves[:35],
            'user': user,
            'sent_love_count': sent_love_count,
            'love_ratio': love_ratio,
            'recieved_love_count': recieved_love_count,
            'logged_in': request.user.is_authenticated()},
    )
