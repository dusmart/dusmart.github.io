import gym
import random

from env import Base2048Env


# Create environment
env = Base2048Env()



# Enjoy trained agent
obs = env.reset()
env.render()
total = 0
for i in range(1000):
    print("mask", env.mask())
    action = random.randint(0, 3)
    obs, rewards, dones, _ = env.step(action)
    total += rewards
    print(Base2048Env.ACTION_STRING[action], "rewards:", rewards, "isDone?", dones, "total_rewards", total)
    if dones and rewards <= 0:
        break
    obs, rewards, dones, info = env.step(action)
    print("ForceToMove,", Base2048Env.ACTION_STRING[action],"rewards:",  rewards, "isDone?", dones)
    env.render()


