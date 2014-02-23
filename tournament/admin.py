from django.http.response import HttpResponse
from django.contrib import admin
from tournament.models import Player
from tournament.models import Game
from tournament.models import Tournament
from tournament.models import Competitor
from django.conf.urls import patterns, url
from django.contrib import messages
from django.db import transaction

class CompetitorInline(admin.StackedInline):
    model = Competitor
    extra = 0
    max_num = 2
    readonly_fields = ('player', 'colour', 'total')


class GameAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'tournament', 'score')
    inlines = [CompetitorInline]
    readonly_fields = ('tournament', 'round')


class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_round', 'rounds_count', 'seed_next_round_column')
    readonly_fields = ('current_round', 'rounds_count')

    def get_urls(self):
        urls = super(TournamentAdmin, self).get_urls()
        my_urls = patterns('',
                           (r'^seed_next_round/$', self.seed_next_round)
        )
        return my_urls + urls

    @transaction.atomic
    def seed_next_round(self, request):
        tournament = Tournament.objects.get(pk=request.POST['id'])
        if (tournament.validate_current_round()):
            tournament.seed_next_round()
            messages.success(request, 'New round has been seeded successfully.')
        else:
            messages.error(request, 'You can\'t seed new round. Make sure previous one has finished.')

        return HttpResponse()

    def seed_next_round_column(self, obj):
        if obj.current_round == obj.rounds_count:
            return 'Tournament completed'
        else:
            return '<a href="#" onclick="django.jQuery.post(\'seed_next_round/\', { id: %d, csrfmiddlewaretoken: document.forms[\'changelist-form\'].csrfmiddlewaretoken.value }, function() { location.reload() });">Seed next round</a>' % (
                obj.id)

    seed_next_round_column.allow_tags = True
    seed_next_round_column.short_description = 'Actions'


admin.site.register(Player)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Game, GameAdmin)