# magestic brawl

a 2-player local fighting game built in python, inspired by street fighter. features a custom game engine built on pygame-ce with a component-based architecture, sprite sheet rendering, frame-based animation, and a state-machine ai opponent.

currently extending the project with a reinforcement learning pipeline — wrapping the game as a gymnasium environment and training an agent via ppo (proximal policy optimization) using stable-baselines3 and self-play.

![Game Preview](assets/demo/demoMB.gif)

## stack

- **language:** python
- **engine:** pygame-ce
- **rl / ml:** gymnasium, stable-baselines3 (ppo), pytorch
- **testing:** pytest, headless smoke tests, deterministic input replay

## highlights

- sprite sheet rendering with per-frame hitbox data for efficient memory usage
- background caching to minimize redraws and maintain consistent frame rate
- state-machine ai with idle, approach, attack, and retreat behaviors
- headless/no-render mode for fast rl training without a display
- gymnasium-compatible environment wrapper (`BrawlEnv`) for agent training

## getting started

### requirements

- python 3.7+
- pygame-ce

### installation

```bash
git clone https://github.com/jlee31/majestic-brawl.git
cd majestic-brawl
pip install pygame-ce
python main.py
```

## controls

### player 1 — warrior

| action | key |
| ------ | --- |
| move | a / d |
| jump | w |
| light attack | r |
| heavy attack | t |

### player 2 — sorcerer

| action | key |
| ------ | --- |
| move | j / l |
| jump | i |
| light attack | o |
| heavy attack | p |

**other controls:** esc to pause, ← / → to switch background, y to toggle auto-scroll

## planned

- add more playable characters
- polish: floating damage numbers, announcer voice clips, volume slider, keybind remapping
- reinforcement learning ai — train a ppo agent via self-play using a gymnasium environment wrapper
