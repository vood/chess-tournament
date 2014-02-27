from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from tournament.models import Tournament

class IndexView(generic.ListView):
    template_name = 'tournament/index.html'

    def get_queryset(self):
        return Tournament.objects.all()

class DetailView(generic.DetailView):
    model = Tournament
    template_name = 'tournament/detail.html'

    def get_queryset(self):
        return Tournament.objects.all().prefetch_related('game_set__player_white', 'game_set__player_black')
