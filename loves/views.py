import datetime
import json
import random

from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render

from loves.models import Love
from users.models import ApprovedEmail

def leaderboards(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    last_weeks_loves = Love.objects.filter(
        creation_time__gt=datetime.datetime.now() - datetime.timedelta(7),
    )

    sender_love_dict = {}
    recipient_love_dict = {}
    for love in last_weeks_loves:
        sender = love.sender
        if sender in sender_love_dict:
            sender_love_dict[sender] += 1
        else:
            sender_love_dict[sender] = 1
        recipient = love.recipient
        if recipient in recipient_love_dict:
            recipient_love_dict[recipient] += 1
        else:
            recipient_love_dict[recipient] = 1

    weekly_loved = sorted(
        recipient_love_dict.items(), key=lambda item: (-1 * item[1])
    )[:10]

    weekly_lovers = sorted(
        sender_love_dict.items(), key=lambda item: (-1 * item[1])
    )[:10]
    
    all_time_lovers_users = ApprovedEmail.objects.annotate(
        num_sent=Count('sent_love')
    ).order_by('-num_sent')[:10]

    all_time_loved_users = ApprovedEmail.objects.annotate(
        num_recieved=Count('recieved_love')
    ).order_by('-num_recieved')[:10]

    all_time_lovers = [(user, user.sent_love.count()) for user in all_time_lovers_users if user.name and user.sent_love.count()]
    all_time_loved = [(user, user.recieved_love.count()) for user in all_time_loved_users if user.name and user.recieved_love.count()]

    return render(
        request,
        'loves/leaderboards.html',
        {
            'all_time_lovers': all_time_lovers,
            'all_time_loved': all_time_loved,
            'weekly_lovers': weekly_lovers,
            'weekly_loved': weekly_loved,
            'logged_in': request.user.is_authenticated(),
        },
    )

def send_love(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))
    users = ApprovedEmail.objects.all()
    formatted_users = []
    for user in users:
        formatted_users.append(
            {
                'label': user.name,
                'id': user.id,
                'value': user.name,
            }
        )
    js_users = json.dumps(formatted_users)
    template_dict = {
        'logged_in': request.user.is_authenticated(),
        'users': js_users,
        'sender_id': request.user.id,
    }

    if request.method == 'POST':
        username = request.POST.get('username', '')
        recipient_id = request.POST.get('recipient_id', '')
        sender_id = request.POST.get('sender_id', '')
        message = request.POST.get('message', '')

        if recipient_id:
            recipients = ApprovedEmail.objects.filter(id=recipient_id)

        if not ((username or recipient_id) and sender_id and message):
            template_dict['message'] = message
            template_dict['recipient_id'] = recipient_id
            template_dict['username'] = username
            template_dict['failure_message'] = 'Fill everything out yo'
        elif not recipient_id or not recipients.count():
            template_dict['message'] = message
            template_dict['failure_message'] = 'You lovin\' an imaginary friend yo'
        elif recipient_id == str(request.user.approvedemail.id):
            template_dict['message'] = message
            template_dict['failure_message'] = (
                'I\'m glad you love yourself. Love someone else! <3')
        else:
            Love.objects.create(
                sender=request.user.approvedemail,
                recipient=recipients[0],
                text=message,
            )
            subject = request.user.first_name + ' sent you love! <3'

            # Trick gmail into not hiding this footer
            num_spaces = random.randint(0, 20)
            footer = "Send love back, or check the leaderboards at www.styleseatlove.com" + " " * num_spaces

            email ='"'+ message+'"' + "\n\n" + footer + "."
            
            send_mail(
                subject,
                email,
                request.user.email,
                [recipients[0].email],
                fail_silently=False,
            )
            
            template_dict['success_message'] = 'Love sent! Send more?'
        return render(
            request,
            'loves/sendlove.html', 
            template_dict,
        )
    else:
        return render(
            request,
            'loves/sendlove.html',
            template_dict,
        )
       
