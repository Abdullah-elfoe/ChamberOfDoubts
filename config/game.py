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


PHASES_COUNT = 3
PHASES = {
    1:[12, 6, 10], # Items, bullets, Health
    2:[3, 8, 6],
    3:[4, 12, 8]
}
