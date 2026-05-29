"""
The smallest possible oTree game — a teaching skeleton.

One player, one round, one decision, no grouping / payoffs / wait pages.
Every oTree app has the same five pieces; this shows them with nothing extra.
"""

from otree.api import *


# 1. CONSTANTS — fixed parameters of the game.
class C(BaseConstants):
    NAME_IN_URL = 'minimal'        # the URL slug oTree serves this under
    PLAYERS_PER_GROUP = None       # None = each participant plays alone (no group, no waiting)
    NUM_ROUNDS = 1                 # single-shot


# 2. DATA MODEL — three nested levels oTree always defines.
#    Subsession = the whole session, Group = a set of interacting players,
#    Player = one participant. We only need a field on Player here.
class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # One decision: a number the participant picks. This is the field the
    # runner's HTML parser will detect and the LLM will fill in.
    number = models.IntegerField(
        min=0, max=100,
        label="Pick a number from 0 to 100.",
    )


# 3. PAGES — the screens a participant sees, in order.
class Decide(Page):
    form_model = 'player'          # the form writes to the Player model
    form_fields = ['number']       # which field(s) appear on this page


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Pass data to the template so it can show the choice back.
        return dict(number=player.number)


# 4. PAGE SEQUENCE — the order oTree walks the participant through.
page_sequence = [Decide, Results]
