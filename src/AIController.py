# level 1 ai
# idles for a random time
# moves toward player if far away from x amount
# randomly trigger attack 1 and 2 
# back off for a short time after getting hit

# the class needs states, timers, updates, and abilities to move
# the ai must instead move the player itself 
# sp itll move vel_x, is_running, jump
# update(fighter, target)

# state timer - how long have i been in this state?

import pygame
from random import randint

class AIController:
    def __init__(self):
        self.state = "idle"
        self.state_timer = 0    # timestamp of when we entered current state
        self.idle_duration = randint(500,2000)  # randomised each time we enter idle

    def update(self, fighter, target):

        elapsed = pygame.time.get_ticks() - self.state_timer

        if fighter.is_hit:
            self.enter_state("retreat")
            elapsed = pygame.time.get_ticks() - self.state_timer  # now reflects new state

        # Virtual inputs - same {action: bool} shape a human's keyboard
        # produces. The AI fills these in based on state, then drives the
        # fighter through move() so it gets gravity, flip, bounds clamping.
        virtual_keys = {
            "left": False,
            "right": False,
            "jump": False,
            "attack1": False,
            "attack2": False,
            "block": False,
        }

        if self.state == "idle":
            if elapsed > self.idle_duration:
                self.enter_state("approach")
                self.idle_duration = randint(500,2000)

        elif self.state == "approach":
            distance = target.rect.x - fighter.rect.x
            if abs(distance) < 200:
                self.enter_state("attack")
            elif distance > 0:
                virtual_keys["right"] = True
            else:
                virtual_keys["left"] = True

        elif self.state == "attack":
            if randint(1, 2) == 1:
                virtual_keys["attack1"] = True
            else:
                virtual_keys["attack2"] = True
            self.enter_state("idle")

        elif self.state == "retreat":
            distance = target.rect.x - fighter.rect.x
            # Move away from the target
            if distance < 0:
                virtual_keys["right"] = True
            else:
                virtual_keys["left"] = True

            if elapsed > 500:
                self.enter_state("idle")

        elif self.state == "jump":
            virtual_keys["jump"] = True

        else:
            self.enter_state("idle")

        fighter.move(target, virtual_keys=virtual_keys)

    def enter_state(self, state): # possible states: idle, approach, attack, jump, retreat
        self.state = state
        self.state_timer = pygame.time.get_ticks()

    
