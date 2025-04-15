import random

class battlecalc:

    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = int(hp)
        self.attack = attack
    
    def attack(self, target):
        damage = random.randint(1, self.attack)
        target.hp -= damage
        print(f"{self.name} attacks {target.name}!")
        print(f"It deals {damage} damage.")

        if target.hp < 0:
            print(f"The enemy is now dead")

