"""
BFI-2 (Big Five Inventory 2) — Soto & John, 2017.
60 items, 5 domains, 15 facets. This is the trait bank that all big5 persona methods draw from.

Sources:
  Paper: Soto, C.J. & John, O.P. (2017). "The Next Big Five Inventory (BFI-2)"
         Journal of Personality and Social Psychology, 113(1), 117-143.
  Items: https://psytests.org/big5/bfiBen-bl.html
  Scoring key & facets: https://lcbc-uio.github.io/questionnaires/articles/bfi-2.html
  Official site: https://www.colby.edu/academics/departments-and-programs/psychology/research-opportunities/personality-lab/the-bfi-2/
"""

DOMAINS = {
    "E": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "N": "Negative Emotionality",
    "O": "Open-Mindedness",
}

FACETS = {
    "E": {
        "sociability":   {"items": [1, 16, 31, 46],  "reverse": [16, 31]},
        "assertiveness": {"items": [6, 21, 36, 51],   "reverse": [36, 51]},
        "energy_level":  {"items": [11, 26, 41, 56],  "reverse": [11, 26]},
    },
    "A": {
        "compassion":     {"items": [2, 17, 32, 47],  "reverse": [17, 47]},
        "respectfulness": {"items": [7, 22, 37, 52],  "reverse": [22, 37]},
        "trust":          {"items": [12, 27, 42, 57], "reverse": [12, 42]},
    },
    "C": {
        "organization":    {"items": [3, 18, 33, 48],  "reverse": [3, 48]},
        "productiveness":  {"items": [8, 23, 38, 53],  "reverse": [8, 23]},
        "responsibility":  {"items": [13, 28, 43, 58], "reverse": [28, 58]},
    },
    "N": {
        "anxiety":              {"items": [4, 19, 34, 49],  "reverse": [4, 49]},
        "depression":           {"items": [9, 24, 39, 54],  "reverse": [9, 24]},
        "emotional_volatility": {"items": [14, 29, 44, 59], "reverse": [29, 44]},
    },
    "O": {
        "intellectual_curiosity": {"items": [10, 25, 40, 55], "reverse": [25, 55]},
        "aesthetic_sensitivity":  {"items": [5, 20, 35, 50],  "reverse": [5, 50]},
        "creative_imagination":   {"items": [15, 30, 45, 60], "reverse": [30, 45]},
    },
}

ITEMS = {
    1:  "Is outgoing, sociable",
    2:  "Is compassionate, has a soft heart",
    3:  "Tends to be disorganized",
    4:  "Is relaxed, handles stress well",
    5:  "Has few artistic interests",
    6:  "Has an assertive personality",
    7:  "Is respectful, treats others with respect",
    8:  "Tends to be lazy",
    9:  "Stays optimistic after experiencing a setback",
    10: "Is curious about many different things",
    11: "Rarely feels excited or eager",
    12: "Tends to find fault with others",
    13: "Is dependable, steady",
    14: "Is moody, has up and down mood swings",
    15: "Is inventive, finds clever ways to do things",
    16: "Tends to be quiet",
    17: "Feels little sympathy for others",
    18: "Is systematic, likes to keep things in order",
    19: "Can be tense",
    20: "Is fascinated by art, music, or literature",
    21: "Is dominant, acts as a leader",
    22: "Starts arguments with others",
    23: "Has difficulty getting started on tasks",
    24: "Feels secure, comfortable with self",
    25: "Avoids intellectual, philosophical discussions",
    26: "Is less active than other people",
    27: "Has a forgiving nature",
    28: "Can be somewhat careless",
    29: "Is emotionally stable, not easily upset",
    30: "Has little creativity",
    31: "Is sometimes shy, introverted",
    32: "Is helpful and unselfish with others",
    33: "Keeps things neat and tidy",
    34: "Worries a lot",
    35: "Values art and beauty",
    36: "Finds it hard to influence people",
    37: "Is sometimes rude to others",
    38: "Is efficient, gets things done",
    39: "Often feels sad",
    40: "Is complex, a deep thinker",
    41: "Is full of energy",
    42: "Is suspicious of others' intentions",
    43: "Is reliable, can always be counted on",
    44: "Keeps their emotions under control",
    45: "Has difficulty imagining things",
    46: "Is talkative",
    47: "Can be cold and uncaring",
    48: "Leaves a mess, doesn't clean up",
    49: "Rarely feels anxious or afraid",
    50: "Thinks poetry and plays are boring",
    51: "Prefers to have others take charge",
    52: "Is polite, courteous to others",
    53: "Is persistent, works until the task is finished",
    54: "Tends to feel depressed, blue",
    55: "Has little interest in abstract ideas",
    56: "Shows a lot of enthusiasm",
    57: "Assumes the best about people",
    58: "Sometimes behaves irresponsibly",
    59: "Is temperamental, gets emotional easily",
    60: "Is original, comes up with new ideas",
}

REVERSE_KEYED = {3, 5, 8, 9, 11, 12, 16, 17, 22, 23, 24, 25, 26, 28, 29,
                 30, 31, 36, 37, 42, 44, 45, 47, 48, 49, 50, 51, 55, 58,
                 4}


def get_domain_items(domain: str) -> list[tuple[int, str, bool]]:
    """Return [(item_num, text, is_reverse)] for a domain."""
    out = []
    for facet_info in FACETS[domain].values():
        for num in facet_info["items"]:
            out.append((num, ITEMS[num], num in REVERSE_KEYED))
    return sorted(out)


def get_facet_items(domain: str, facet: str) -> list[tuple[int, str, bool]]:
    """Return [(item_num, text, is_reverse)] for a specific facet."""
    info = FACETS[domain][facet]
    return [(num, ITEMS[num], num in REVERSE_KEYED) for num in info["items"]]


def score_domain(responses: dict[int, int], domain: str) -> float:
    """Score a domain (1-5) from item responses (1-5 each)."""
    items = get_domain_items(domain)
    total = 0
    for num, _, is_reverse in items:
        val = responses[num]
        total += (6 - val) if is_reverse else val
    return total / len(items)
