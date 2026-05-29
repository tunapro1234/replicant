import re
from os import environ
from pathlib import Path


def _discover_session_configs():
    """Auto-build one session config per oTree app folder.

    An "app" is any subdirectory here with an __init__.py that defines
    NAME_IN_URL. num_demo_participants is read from PLAYERS_PER_GROUP
    (None or 1 -> 1). Drop a game folder in and restart — no manual edit.

    (For multi-app sequences you'd still hand-write a config; single-app
    games, which is all we run, are discovered automatically.)
    """
    base = Path(__file__).resolve().parent
    configs = []
    for app in sorted(p for p in base.iterdir() if p.is_dir()):
        if app.name.startswith(("_", ".")):
            continue
        init = app / "__init__.py"
        if not init.exists():
            continue
        src = init.read_text()
        if "NAME_IN_URL" not in src:
            continue
        m = re.search(r"PLAYERS_PER_GROUP\s*=\s*(\w+)", src)
        ppg = m.group(1) if m else "None"
        n = int(ppg) if ppg.isdigit() else 1
        configs.append(dict(name=app.name, app_sequence=[app.name],
                            num_demo_participants=n))
    return configs


SESSION_CONFIGS = _discover_session_configs()

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'admin')

OTREE_REST_KEY = environ.get('OTREE_REST_KEY', 'test-rest-key')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '8137439220110'

INSTALLED_APPS = ['otree']
