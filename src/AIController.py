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
        elapsed = pygame.time.get_ticks() - self.state_timer  # e.g. 300ms later = 300
        if elapsed > self.idle_duration:
            self.enter_state("approach")  # done waiting, go do something

    def enter_state(self, state): # possible states: idle, approach, attack, jump
        self.state = state
        self.state_timer = pygame.time.get_ticks() - self.state_timer

    
