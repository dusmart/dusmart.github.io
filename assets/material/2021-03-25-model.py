import gym
import random


from stable_baselines import DQN, PPO2
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines.common.policies import FeedForwardPolicy

from env import Base2048Env
import numpy as np
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.policies import LstmPolicy


class CustomPolicy(FeedForwardPolicy):
	def __init__(self, *args, **kwargs):
		super(CustomPolicy, self).__init__(*args, **kwargs,net_arch=[dict(pi=[128, 128, 128],vf=[128, 128, 128])],feature_extraction="mlp")

# Create environment
env = Base2048Env()
#model = PPO2(CustomPolicy, env, verbose=0, tensorboard_log='tensorboard_log')



## Instantiate the agent
#model = DQN(MlpPolicy, env, learning_rate=1e-4, prioritized_replay=True, verbose=1, buffer_size=50000)
model = DQN.load("dqn3")
#model.set_env(env)
#model.learning_rate = 1e-5
#model.exploration_initial_eps=0.2
#model.exploration_final_eps=0.01
 # Train the agent
#model.learn(total_timesteps=int(4e5))
# # Save the agent
#model.save("dqn3")
#del model  # delete trained model to demonstrate loading

#Load the trained agent
#model = PPO2.load("dqn_lunar4")

# Evaluate the agent
# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

# Enjoy trained agent
obs = env.reset()
env.render()
total = 0
for i in range(1000):
    print("mask", env.mask())
    action, _states = model.predict(obs)
    prob = model.action_probability(obs)
    print("prob", prob, "mask", env.mask())
    for i, mask in enumerate(env.mask()):
        prob[i] *= mask
    action = np.argmax(prob)
    obs, rewards, dones, _ = env.step(action)
    total += rewards
    print(Base2048Env.ACTION_STRING[action], "rewards:", rewards, "isDone?", dones, "total_rewards", total)
    env.render()
    if dones and rewards <= 0:
        break