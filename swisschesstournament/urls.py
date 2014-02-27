from django.conf.urls import patterns, include, url
from tournament import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view()),
    url(r'^tournament/', include('tournament.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
