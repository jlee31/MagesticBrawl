planned additions:

- homescreen + settings menu
- particles / effects
- ability to play other characters
- loading / 3 2 1
- movable background (DONE)
- Announcer Voice Clips

“Round 1... Fight!”, “K.O.”, character names, win calls.
- pause

maybe

- score counter


IN ORDER:
1) Add pygame masks for proper collisions (DONE)
2) add particles
3) add homescreen + menu + countdown
4) ability to play other characters



HIT ANIMATION CALL STACK:

1. ATTACK TRIGGERED:
   - Player presses attack key (R/T for Player 1, O/P for Player 2)
   - move() method calls attack() method
   - attack() sets self.attacking = True and self.attack_type = 1 or 2

2. ATTACK ANIMATION STARTS:
   - updateAction() detects self.attacking = True
   - Calls update_action(3) for Attack 1 or update_action(4) for Attack 2
   - Animation changes to attack pose (action 3 or 4)

3. COLLISION DETECTION (EVERY FRAME):
   - level.py run() method calls checkAttackCollision() every frame
   - checkAttackCollision() checks if masks overlap
   - If collision occurs: target.health -= 10 and target.is_hit = True

4. HIT ANIMATION TRIGGERED:
   - Target's updateAction() detects self.is_hit = True
   - Calls update_action(5) to start hit animation
   - Animation changes to hit pose (action 5)

5. HIT ANIMATION PLAYS:
   - updateFrame() shows hit animation frames
   - handleAnimationComplete() waits for hit animation to finish

6. HIT ANIMATION ENDS:
   - When frame_index reaches end of hit animation
   - handleAnimationComplete() sets self.is_hit = False
   - Character returns to normal state (idle, run, etc.)

KEY FUNCTIONS IN ORDER:
   move() → attack() → updateAction() → update_action(3/4) → 
   checkAttackCollision() → target.is_hit = True → 
   target.updateAction() → target.update_action(5) → 
   target.handleAnimationComplete() → target.is_hit = False