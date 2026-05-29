"""
Charness & Rabin (2002) allocation games — Horton 'Homo Silicus' Experiment 2.

Person B (the decider) chooses Left/Right across 6 scenarios, one per round.
Single player. Round order matches replication/homo_silicus/charness_rabin.py
so the oTree run can be compared against the no-oTree replication.
"""

from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'charness_rabin'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6
    # round -> name + payoffs. a = Person A, b = the decider (Person B).
    SCENARIOS = {
        1: dict(name="Berk29", left_a=400, left_b=400, right_a=750, right_b=400),
        2: dict(name="Barc2",  left_a=400, left_b=400, right_a=750, right_b=375),
        3: dict(name="Berk23", left_a=800, left_b=200, right_a=0,   right_b=0),
        4: dict(name="Barc8",  left_a=300, left_b=600, right_a=700, right_b=500),
        5: dict(name="Berk15", left_a=200, left_b=700, right_a=600, right_b=600),
        6: dict(name="Berk26", left_a=0,   left_b=800, right_a=400, right_b=400),
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField(
        choices=[["Left", "Left"], ["Right", "Right"]],
        widget=widgets.RadioSelect,
        label="What do you choose?",
    )


class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(s=C.SCENARIOS[player.round_number],
                    round=player.round_number, total=C.NUM_ROUNDS)


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Decision, Results]
