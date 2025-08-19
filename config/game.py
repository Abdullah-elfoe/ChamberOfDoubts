INVENTORY_ITEMS = ["Injection", "Bazuka", "Clock", "Glasses"]
SPECIAL_ITEMS = ["Switch", "Fishing Rod", "Pill", "Signal Jammer"]
TOTAL_ITEMS = len(INVENTORY_ITEMS+SPECIAL_ITEMS)

    # to switch bullets, To steal, to increase or decrease health,

PATHS = {
    "Glasses": "assets/images/items/glasses.png",
    "Injection": "assets/images/items/injection.png",
    "Clock":"assets/images/items/clock.png",
    "Bazuka": "assets/images/items/bazooka.png",
    "Signal Jammer":"assets/images/items/signalJammer.png",
    "Switch": "assets/images/items/switch.png",
    "Fishing Rod": "assets/images/items/fishing-rod.png",
    "Pill":"assets/images/items/pill.png",
}

CONTROLS_PATH = {
    "Inventory": "assets/images/general/box.png",
    "Shoot": "assets/images/general/shoot.png",
    "Messages":"assets/images/general/messages.png"
}

DESCRIPTION = {
    "Glasses": "Lets you peek inside the current chamber. Reveals whether the next shot is live or safe",
    "Injection": "A quiet relief in chaos. Restores 1 bar of health — no gamble, no pain, just a moment of peace in a bloodstained game",
    "Clock":"Skips the opponent’s next turn. Gives you a strategic advantage when timed well.",
    "Bazuka": "Unleashes brutal force, tearing through two bars of life in one strike. It doesn’t just hurt — it scars.",
    "Signal Jammer":"Removes the current loaded shell from the chamber. The next shell immediately takes its place.",
    "Switch": "Swaps your chamber with your opponent’s. Dangerous and clever—use when you suspect a bullet.",
    "Fishing Rod": "Steals a random item from the opponent. Can turn the tide if you grab the right tool.",
    "Pill":"A silent gamble. Swallow it, and feel your body mend — or take your health 1 bar",
}


PHASES_COUNT = 3
PHASES = {
    1:[3, 5, 5], # Items, bullets, Health
    2:[3, 6, 6],
    3:[6, 7, 7]
}
