from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User as AuthUser
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login, logout
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from users.models import ApprovedEmail


def change_password(request):
    template_response = views.password_change(request)
    return template_response

def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    else:
        return login(request)

def custom_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/') 

def homepage(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
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
        return HttpResponseRedirect('/profile/' + user.first_name + '_' + user.last_name)


def profile(request, fullname=None):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))
    if fullname:
        name_chunks = fullname.split('_')
        users = AuthUser.objects.filter(first_name=name_chunks[0], last_name=name_chunks[1])
        if not users:
            raise Http404('User does not exist')
        user = users[0]
    else:
        user = AuthUser.objects.get(id=request.user.id)
    sent_loves = user.sent_love.order_by('-id')
    recieved_loves = user.recieved_love.order_by('-id')
    return render(
        request,
        'users/profile.html', 
        {'sent_loves': sent_loves, 'recieved_loves': recieved_loves, 'logged_in': request.user.is_authenticated()},
    )
