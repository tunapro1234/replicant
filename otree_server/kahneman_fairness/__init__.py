"""
Kahneman, Knetsch & Thaler (1986) price-fairness task — Horton et al. "Homo
Silicus" Experiment 1 (arXiv:2301.07543).

A store raises snow-shovel prices after a blizzard; the participant rates the
action on a 4-point fairness scale. Single player, one decision.

Original KKT (1986): for the $15 -> $20 increase, ~82% of people rated it
unfair or very unfair. Horton showed the rating shifts with political persona
(left = unfair, right = acceptable) and rises with the size of the increase.

Prompt text matches kkt.py from github.com/johnjosephhorton/homo_silicus.
"""

from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'kahneman_fairness'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    fairness = models.IntegerField(
        choices=[
            [1, "Completely Fair"],
            [2, "Acceptable"],
            [3, "Unfair"],
            [4, "Very Unfair"],
        ],
        widget=widgets.RadioSelect,
        label="Please rate this action:",
    )


class Scenario(Page):
    form_model = 'player'
    form_fields = ['fairness']


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(rating=player.field_display('fairness'))


page_sequence = [Scenario, Results]
