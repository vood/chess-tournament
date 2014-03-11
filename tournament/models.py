from django.db import models, connection
from django.db.models import Sum, Q
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
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
        games = self.game_set.filter(round=self.current_round, is_rated=False).all()
        for game in games:
            game.rate_players()

        games.update(is_rated=True)

        self._update_stats()

        self.current_round += 1

        if (self.current_round == 1):
            players = Player.objects.all()
        else:
            players = Player.objects \
                .filter(stats__game__tournament=self, stats__game__round__lt=self.current_round) \
                .annotate(total=Sum("stats__score")) \
                .order_by('-total', '-rating')

        i = 0

        games = map(lambda x: (x.player_white_id, x.player_black_id), list(self.game_set.all()))
        sorted = []

        for player1 in players:
            if player1.id in sorted:
                continue
            game = Game()
            game.tournament = self
            game.round = self.current_round
            for player2 in players:
                if player2.id in sorted or player1.id == player2.id:
                    continue
                if ((player1.id, player2.id) in games) == False:
                    game.player_white = player1
                    game.player_black = player2
                    game.save()
                    games.append((player1.id, player2.id))
                    sorted.append(player1.id)
                    sorted.append(player2.id)
                    break
                elif ((player2.id, player1.id) in games) == False:
                    game.player_white = player2
                    game.player_black = player1
                    games.append((player2.id, player1.id))
                    game.save()
                    sorted.append(player1.id)
                    sorted.append(player2.id)
                    break


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
        return self.game_set.filter(score__isnull=True).count() == 0

    def __unicode__(self):
        return self.name

    def _update_stats(self):
        sql = '''
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_white_id, 1 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 3;
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_black_id, 1 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 2;
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_white_id, 0.5 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 1;
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_black_id, 0.5 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 1;
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_white_id, 0 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 2;
INSERT INTO tournament_stats (game_id, player_id, score) SELECT id, player_black_id, 0 FROM tournament_game WHERE round = %d AND tournament_id = %d AND score = 3;
        ''' % (
            self.current_round,
            self.id,
            self.current_round,
            self.id,
            self.current_round,
            self.id,
            self.current_round,
            self.id,
            self.current_round,
            self.id,
            self.current_round,
            self.id)
        cursor = connection.cursor()
        cursor.execute(sql)

    def results(self):
        return Player.objects \
                .filter(stats__game__tournament=self) \
                .annotate(total=Sum("stats__score")) \
                .order_by('-total', '-rating')

    def rounds_list(self):
        return range(1, self.rounds_count + 1)


class Player(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField(validators=[MinValueValidator(0)], default=0)

    def __unicode__(self):
        return self.name

    def update_rating(self, competitor_rating, score):
        ea = 1 / (1 + math.pow(10, (self.rating - competitor_rating) / 400))
        self.rating = round(self.rating + self._get_k(self.rating) * (score - ea))
        self.save()

    def _get_k(self, rating):
        k = 0
        if rating >= 2400:
            k = 10
        elif rating >= 30:
            k = 15
        else:
            k = 30
        return k

    class Meta:
        ordering = ('-rating',)


class Game(models.Model):
    SCORES = (
        (3, _("Won-Lost (1:0)")),
        (2, _("Lost-Won (0:1)")),
        (1, _("Tie (0.5:0.5)"))
    )

    is_rated = models.BooleanField(default=False)
    round = models.PositiveIntegerField()
    tournament = models.ForeignKey("Tournament")
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(3)], null=True, choices=SCORES)
    player_white = models.ForeignKey("Player", related_name="white_games")
    player_black = models.ForeignKey("Player", related_name="black_games")

    class Meta:
        ordering = ('round',)

    def __unicode__(self):
        return _("Round #%d (%s vs %s)") % (self.round, self.player_white, self.player_black)

    def rate_players(self):
        if self.is_rated == False:
            rating1 = self.player_white.rating
            rating2 = self.player_black.rating

            self.player_white.update_rating(rating2, self.score_black())
            self.player_black.update_rating(rating1, self.score_white())

    def score_black(self):
        if self.score == 3:
            return 0
        elif self.score == 2:
            return 1
        else:
            return 0.5

    def score_white(self):
        if self.score == 3:
            return 1
        elif self.score == 2:
            return 0
        else:
            return 0.5


class Stats(models.Model):
    player = models.ForeignKey("Player")
    game = models.ForeignKey("Game")
    score = models.FloatField(validators=[MinValueValidator(0)], default=0)


