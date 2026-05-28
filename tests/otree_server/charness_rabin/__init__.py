from otree.api import *

doc = """
Charness & Rabin (2002) allocation games, as used in Horton et al.
"Homo Silicus" (arXiv:2301.07543).

Person B (the decider) chooses between two allocations for themselves
and Person A. Six scenarios with different payoff structures testing
self-interest vs fairness vs efficiency.

Source: charness_rabin.py from github.com/johnjosephhorton/homo_silicus
"""


class C(BaseConstants):
    NAME_IN_URL = 'charness_rabin'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6

    SCENARIOS = {
        1: {"name": "Berk29",  "left_a": 400, "left_b": 400, "right_a": 750, "right_b": 400},
        2: {"name": "Barc2",   "left_a": 400, "left_b": 400, "right_a": 750, "right_b": 375},
        3: {"name": "Berk23",  "left_a": 800, "left_b": 200, "right_a": 0,   "right_b": 0},
        4: {"name": "Barc8",   "left_a": 300, "left_b": 600, "right_a": 700, "right_b": 500},
        5: {"name": "Berk15",  "left_a": 200, "left_b": 700, "right_a": 600, "right_b": 600},
        6: {"name": "Berk26",  "left_a": 0,   "left_b": 800, "right_a": 400, "right_b": 400},
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


def set_payoffs(player: Player):
    s = C.SCENARIOS[player.round_number]
    if player.choice == "Left":
        player.payoff = cu(s["left_b"])
    else:
        player.payoff = cu(s["right_b"])


class Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player: Player):
        s = C.SCENARIOS[player.round_number]
        return dict(
            scenario_name=s["name"],
            round=player.round_number,
            total_rounds=C.NUM_ROUNDS,
            left_a=s["left_a"],
            left_b=s["left_b"],
            right_a=s["right_a"],
            right_b=s["right_b"],
        )


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        choices = []
        for p in player.in_all_rounds():
            s = C.SCENARIOS[p.round_number]
            choices.append({"round": p.round_number, "name": s["name"], "choice": p.choice})
        return dict(choices=choices)


page_sequence = [Decision, Results]
