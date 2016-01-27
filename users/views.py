from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User as AuthUser
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from users.models import ApprovedEmail


def change_password(request):
    template_response = views.password_change(request)
    return template_response


def signup(request):
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
                        If you have and are experiencing this error, contact Bryce to \
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
        user = AuthUser.objects.create_user(
            approved_email.email,  # we're using the email as username, too
            email=approved_email.email,
            password=password,
            first_name=approved_email.first_name,
            last_name=approved_email.last_name,
            )
        return HttpResponseRedirect('/user/' + user.first_name + user.last_name)


def profile(request, fullname):
    name_chunks = fullname.split('-')
    users = AuthUser.objects.filter(first_name=name_chunks[0], last_name=name_chunks[1])
    if not users:
        raise Http404("User does not exist")
    user = user[0]
    sent_loves = user.sent_love_set.order_by('creation_date')
    recieved_loves = user.recieved_love_set.order_by('creation_date')
    return render(
        request,
        'users/profile.html', 
        {sent_loves: sent_loves, recieved_loves: recieved_loves},
    )
