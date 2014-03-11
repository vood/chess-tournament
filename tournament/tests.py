from django.test import TestCase
from tournament.models import Tournament, Game, Player, Stats

class TournamentTestCase(TestCase):
    def test_validate_current_round(self):
        tournament = Tournament()
        self.assertTrue(tournament.validate_current_round())

    def test__calculate_number_of_rounds(self):
        tournament = Tournament()
        self.assertEqual(tournament._calculate_number_of_rounds(), 0)

class GameTestCase(TestCase):
    def test_score_black(self):
        game = Game()
        game.score = 3
        self.assertEqual(game.score_black(), 0)
        game.score = 2
        self.assertEqual(game.score_black(), 1)
        game.score = 1
        self.assertEqual(game.score_black(), 0.5)

    def test_score_black(self):
        game = Game()
        game.score = 3
        self.assertEqual(game.score_white(), 1)
        game.score = 2
        self.assertEqual(game.score_white(), 0)
        game.score = 1
        self.assertEqual(game.score_white(), 0.5)


class PlayerTestCase(TestCase):
    def test___get_k(self):
        player = Player()
        self.assertEqual(player._get_k(2600), 10)
        self.assertEqual(player._get_k(30), 15)
        self.assertEqual(player._get_k(1), 30)
