import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

from operator import itemgetter

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here

        self.q_value = {} # q value table

        self.epsilon = 0.1   

        self.gamma = 0.1  # discount factor

        self.alpha = 0.5 # learning rate

        self.q_init = 5.0 # initial q value - Optimistic

        self.reward = 0  # initial reward

        self.state = None

        self.step = 0

        self.total_reward = 0

        self.penalty = 0


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

        self.state = None
        self.action = None
        self.step = 0
        self.total_reward = 0
        self.penalty = 0


    def get_max_q(self, state):
        """return the max q value in next state"""
        q_max = max([self.q_value[state][action] for action in self.q_value[state]])
        return q_max


    def update_q_value(self, state, action, new_state, reward):
        """calculate q value based on the choosen action"""

        max_q = self.get_max_q(new_state)
        
        # q learning formula
        self.q_value[state][action] = round((1 - self.alpha) * self.q_value[state][action] + self.alpha * (reward + self.gamma * max_q), 2)
            

    def get_action(self, state):
        """Select action according to the policy"""

        if random.random() < self.epsilon:
            action = random.choice(Environment.valid_actions)

        else:
            # get Q value table in the given state
            Qtable = self.q_value[state]

            # choose the action with the maximum Q value
            action = max(Qtable.iteritems(), key=itemgetter(1))[0]
            # print "action is ", action

        return action


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state

        # action = self.next_waypoint
        # self.next_waypoint = random.choice(Environment.valid_actions)
        # reward = self.env.act(self, action)



        self.new_state = (  ("directions",self.next_waypoint),
                        ("light",inputs['light']),
                        ("oncoming", inputs['oncoming']),
                        ("left",inputs['left']))

        # initialize q value table
        if self.new_state not in self.q_value.viewkeys():
            self.q_value[self.new_state] = {}
            for act in Environment.valid_actions:
                if act not in self.q_value[self.new_state]:
                    self.q_value[self.new_state][act] = self.q_init


        # TODO: Select action according to your policy
        action = self.get_action(self.new_state)
        
        # Execute action and get reward
        new_reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.step > 0:
            # print "q table is : ", self.q_value
            self.update_q_value(self.state, self.action, self.new_state, self.reward)

        self.action = action
        self.state = self.new_state
        self.reward = new_reward
        self.step += 1
        self.total_reward += new_reward

        # Count values for result analysis
        # if (new_reward < 0):
        #     self.penalty += 1
        # print "Negative reward: inputs = {}, action = {}, penalty = {}, reward = {}, waypoint {}".format(inputs, action, self.penalty, new_reward, self.next_waypoint)

        # diaplay Q-table
        # print self.q_value
        for i in self.q_value:
            if action != self.next_waypoint:
                print i, self.q_value[i]

        # print "total_reward", self.total_reward
        # print "Q-table", self.q_value
        # print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, new_reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.001, display=False, live_plot=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
