# -*- coding: utf-8 -*-
# @Author: shubham
# @Date:   2017-01-10 19:37:24
# @Last Modified by:   shubham
# @Last Modified time: 2017-01-11 01:21:24

import gym
from gym import wrappers

import pandas as pd
import numpy as np

import sys
import random
import itertools
from pprint import pprint
from collections import defaultdict

class Agent(object):
	def __init__(self, nA=4, epsilon=0.5, epsilon_decay=0.99, alpha=0.2, gamma=1):
		self.nA = nA
		self.epsilon = epsilon
		self.epsilon_decay = epsilon_decay
		self.alpha = alpha
		self.gamma = gamma
		self.Q = defaultdict(lambda: np.random.uniform(low=-1, high=1, size=nA))
	

	def policy(self, state):
		# select greedy action
		action_selected = np.argmax(self.Q[state])
		
		# assign epsilon prob to each action
		action_prob = np.full(self.nA, self.epsilon/self.nA)
		action_prob[action_selected] += (1-self.epsilon)

		# select an action base on prob
		action = np.random.choice(self.nA, p=action_prob)

		return action

	def set_initial_state(self, state):
		self.state = state
		self.action = self.policy(state)
		# print(len(self.Q.keys()))
		
		# decay epsilon
		self.epsilon *= self.epsilon_decay
		return self.action
	
	def act(self, next_state, reward):
		state = self.state
		action = self.action
		alpha = self.alpha
		gamma = self.gamma

		# TD Update
		td_target = reward + gamma * np.max(self.Q[next_state])
		td_error = td_target - self.Q[state][action]
		self.Q[state][action] += alpha * td_error
		
		# select next action eps-greedy
		next_action = self.policy(next_state)
		self.state = next_state
		self.action = next_action
		return self.action


def build_state(observation):
	bins_range = [(-2.4, 2.4), (-2, 2), (-1, 1), (-3.5, 3.5)]
	bins = [np.linspace(mn, mx, 11)[1:-1] for mn, mx in bins_range]
	
	state = ''
	for feature, _bin in zip(observation, bins):
		state += str(np.digitize(feature, _bin))
	return state

def main():
	env = gym.make('CartPole-v0')
	outdir = './experiment-results'
	env = wrappers.Monitor(env, directory=outdir, force=True, video_callable=False)

	agent = Agent(env.action_space.n)
	total_t = 0
	for i_episode in range(50000):
		observation = env.reset()
		state = build_state(observation)
		action = agent.set_initial_state(state)

		for t in range(200):
			next_ob, reward, done, info = env.step(action)
			next_state = build_state(next_ob)

			if done: reward = -200
			action = agent.act(next_state, reward)
			if done:
				break

		total_t += t
		if (i_episode + 1) % 100 == 0:
			print("\rEpisode: {}, Reward: {}".format(i_episode + 1, total_t/(i_episode+1)), end="")
			sys.stdout.flush()
	
	env.close()
	gym.upload(outdir, api_key='sk_9YxUhFDaT5XSahcLut47w')


if __name__ == '__main__':
	main()

