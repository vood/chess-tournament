from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
import itertools
import math


class Tournament(models.Model):
    name = models.CharField(max_length=255)
    rounds_count = models.PositiveIntegerField(default=0)
    current_round = models.PositiveIntegerField(default=0)

    def seed_next_round(self):
        count = Player.objects.count()
        if (self.current_round == self.rounds_count or count < 2):
            return
        self.current_round += 1
        players = Player.objects.order_by('-rating')
        i = 0
        while i < count:
            game = Game.objects.create(tournament=self, round=self.current_round)
            if players[i + 1]:
                Competitor.objects.create(player=players[i], game=game, colour=True)
                Competitor.objects.create(player=players[i + 1], game=game, colour=False)
            else:
                Competitor.objects.create(player=players[i], score=1, game=game, colour=True)
            i += 2
        super(Tournament, self).save()

    def save(self, force_insert=False, force_update=False, using=None):
        self.rounds_count = self._calculate_number_of_rounds()
        super(Tournament, self).save(force_insert, force_update, using)

    def _calculate_number_of_rounds(self):
        count = Player.objects.count()
        return round(math.sqrt(count + 2 * (count - 1)))

    def rounds(self):
        g = itertools.groupby(list(self.game_set.all()), lambda x: x.round)
        #workaround for django templates  http://stackoverflow.com/questions/6906593/itertools-groupby-in-a-django-template
        return [(round, list(games)) for round, games in g]

    def validate_current_round(self):
        return self.game_set.filter(competitor__score__isnull=True).count() == 0

    def __unicode__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField(validators=[MinValueValidator(0)], default=0)

    def __unicode__(self):
        return self.name


class Game(models.Model):
    round = models.PositiveIntegerField()
    tournament = models.ForeignKey("Tournament")
    players = models.ManyToManyField("Player", through="Competitor")

    class Meta:
        ordering = ('round',)

    def __unicode__(self):
        return "Round #%d (%s vs %s)" % (self.round, self.player1(), self.player2())

    def player1(self):
        return self.players.all()[0]

    def player2(self):
        return self.players.all()[1]

    def score(self):
        items = list(self.competitor_set.all())
        return ':'.join(map(lambda x: str(x.score), items))

    def player1_total(self):
        return self.competitor_set.all()[0].total

    def player2_total(self):
        return self.competitor_set.all()[1].total

class Competitor(models.Model):
    COLOURS = (
        (True, 'White'),
        (False, 'Black')
    )
    SCORES = (
        (0.0, "Lost"),
        (1.0, "Won"),
        (0.5, "Tie")
    )

    def __unicode__(self):
        return self.player

    def save(self, force_insert=False, force_update=False, using=None):
        self.total = Competitor.objects.filter(player=self.player, game__tournament=self.game.tournament,
                                               game__round__lt=self.game.round).aggregate(
            total=Sum('score'))['total']
        if self.total == None:
            self.total = 0
        super(Competitor, self).save(force_insert, force_update, using)


    player = models.ForeignKey("Player")
    game = models.ForeignKey("Game")
    colour = models.BooleanField(choices=COLOURS, default=True)
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], null=True, choices=SCORES)
    total = models.FloatField(validators=[MinValueValidator(0)], default=0)

