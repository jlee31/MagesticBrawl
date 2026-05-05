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

        if self.state == "idle":
            fighter.is_running = False
            if elapsed > self.idle_duration:
                self.enter_state("approach")
                self.idle_duration = randint(500,2000)

        elif self.state == "approach":
            distance = target.rect.x - fighter.rect.x
            fighter.flip = distance < 0
            if abs(distance) < 200:
                self.enter_state("attack")

            if distance > 200:
                fighter.rect.x += 10
                fighter.is_running = True

            if distance < -200:
                fighter.rect.x -= 10
                fighter.is_running = True

        elif self.state == "attack":
            fighter.is_running = False
            attack_type = randint(1,2)
            fighter.attack_type = attack_type
            fighter.attack(pygame.display.get_surface(), target)
            self.enter_state("idle")

        elif self.state == "retreat":
            distance = target.rect.x - fighter.rect.x
            fighter.flip = distance < 0
            if distance < 0:
                fighter.rect.x += 10
                fighter.is_running = True

            if distance > 0:
                fighter.rect.x -= 10
                fighter.is_running = True

            if elapsed > 500:
                self.enter_state("idle")

        elif self.state == "jump":
            pass

        else:
            self.enter_state("idle")

    def enter_state(self, state): # possible states: idle, approach, attack, jump, retreat
        self.state = state
        self.state_timer = pygame.time.get_ticks()

    
