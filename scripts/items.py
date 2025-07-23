from random import choice


def Injection(obj):
    obj.template.myHealthBar.heal()

def Bazuka(obj):
    obj.increaseDamage()

def Glasses(obj):
    obj.template.infoBooth.text = f"Bullet {"" if obj.bullets[0] else "not"} Found" 
    obj.template.infoBooth.permission = True

def fishingRod(obj):
    obj.template.opponentInventory.hoverPermission= True



def Clock(obj):
    obj.clockUsed = True

def Switch(obj):
    if obj.bullets[0]:
        obj.bullets[0] = False
    else:
        obj.bullets[0] = not False

def SignalJammer(obj):
    obj.bullets.pop(0)

def Pill(obj):
    hit = choice([True, False])
    if hit:
        obj.template.myHealthBar.hit()
    else:
        Injection(obj)
    



function_list = {
    "Injection":[Injection,None],
    "Bazuka":[Bazuka, None],
    "Glasses":[Glasses, None],
    "Clock":[Clock, None],
    "Fishing Rod":[fishingRod, None],
    "Switch":[Switch, None],
    "Signal Jammer":[SignalJammer, None],
    "Pill":[Pill, None],

}