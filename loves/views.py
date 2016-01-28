import json

from django.contrib.auth.models import User as AuthUser
from django.shortcuts import render

from loves.models import Love

def leaderboards(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))
    all_time_lovers = []
    all_time_loved = []
    weekly_lovers = []
    weekly_loved = []
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
    users = AuthUser.objects.all()
    formatted_users = []
    for user in users:
        name = user.first_name + ' ' + user.last_name
        formatted_users.append(
            {
                'label': name,
                'id': user.id,
                'value': name,
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
            recipients = AuthUser.objects.filter(id=recipient_id)

        if not ((username or recipient_id) and sender_id and message):
            template_dict['message'] = message
            template_dict['recipient_id'] = recipient_id
            template_dict['username'] = username
            template_dict['failure_message'] = 'Fill everything out yo'
        elif not recipient_id or not recipients.count():
            template_dict['message'] = message
            template_dict['failure_message'] = 'You lovin\' an imaginary friend yo'
        elif recipient_id == str(request.user.id):
            template_dict['message'] = message
            template_dict['failure_message'] = 'I\'m glad you love yourself. Love someone else! <3'
        else:
            Love.objects.create(
                sender=request.user,
                recipient=recipients[0],
                text=message,
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
       
