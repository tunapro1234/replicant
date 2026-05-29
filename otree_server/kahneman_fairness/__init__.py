from otree.api import *

doc = """
Kahneman, Knetsch & Thaler (1986) fairness perception task, as used in
Horton et al. "Homo Silicus" (arXiv:2301.07543).

A store raises prices after a snowstorm. Participant rates the action
on a 4-point fairness scale. Single player, no interaction.

Source: kkt.py from github.com/johnjosephhorton/homo_silicus
"""


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
