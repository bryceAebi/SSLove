"""sslove URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from loves import views as loves_views
from users import views as users_views

urlpatterns = [
    url(r'^login/$', users_views.custom_login),
    url(r'^logout/$', users_views.custom_logout),
    url(r'^admin/', admin.site.urls),
    url(r'^signup/$', users_views.signup, name='signup'), 
    url(r'^profile/(?P<fullname>[a-zA-Z0-9_]*)/$', users_views.profile, name='profile'),
    url(r'^profile/$', users_views.profile, name='own_profile'),
    url(r'^sendlove/$', loves_views.send_love, name='sendlove'),
    url(r'^leaderboards/$', loves_views.leaderboards, name='leaderboards'),
    url('^', include('django.contrib.auth.urls')),
    url('^$', users_views.homepage, name='homepage'),
]
