import numpy as np
from typing import List, Dict
import random

class QLearningRouteOptimizer:
    def __init__(self, n_locations: int, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 1.0,
                 epsilon_decay: float = 0.995, min_epsilon: float = 0.01):
        self.n_locations = n_locations
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.q_table = {}
        
    def get_state(self, visited: List[int], current: int) -> str:
        return f"{current}_{','.join(map(str, sorted(visited)))}"
    
    def get_available_actions(self, visited: List[int]) -> List[int]:
        return [i for i in range(self.n_locations) if i not in visited]
    
    def choose_action(self, state: str, available_actions: List[int]) -> int:
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(available_actions)
        
        q_values = {action: self.q_table[state].get(action, 0) 
                   for action in available_actions}
        return max(q_values, key=q_values.get)
    
    def update_q_value(self, state: str, action: int, reward: float, next_state: str):
        if state not in self.q_table:
            self.q_table[state] = {}
        
        current_q = self.q_table[state].get(action, 0)
        
        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
        else:
            max_next_q = 0
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, distance: float, is_urgent: bool) -> float:
        base_reward = -distance
        if is_urgent:
            base_reward *= 1.5
        return base_reward
    
    def train(self, distance_matrix: np.ndarray, priorities: List[bool], 
              n_episodes: int = 1000) -> List[Dict]:
        training_logs = []
        
        for episode in range(n_episodes):
            visited = [0]
            current = 0
            total_reward = 0
            total_distance = 0
            
            while len(visited) < self.n_locations:
                state = self.get_state(visited, current)
                available_actions = self.get_available_actions(visited)
                
                if not available_actions:
                    break
                
                action = self.choose_action(state, available_actions)
                distance = distance_matrix[current][action]
                is_urgent = priorities[action]
                reward = self.calculate_reward(distance, is_urgent)
                
                visited.append(action)
                next_state = self.get_state(visited, action)
                self.update_q_value(state, action, reward, next_state)
                
                total_reward += reward
                total_distance += distance
                current = action
            
            total_distance += distance_matrix[current][0]
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            
            if episode % 50 == 0:
                training_logs.append({
                    'episode': episode,
                    'total_reward': float(total_reward),
                    'epsilon': float(self.epsilon),
                    'average_distance': float(total_distance)
                })
        
        return training_logs
    
    def get_optimized_route(self, distance_matrix: np.ndarray, 
                           priorities: List[bool]) -> List[int]:
        visited = [0]
        current = 0
        
        while len(visited) < self.n_locations:
            state = self.get_state(visited, current)
            available_actions = self.get_available_actions(visited)
            
            if not available_actions:
                break
            
            if state in self.q_table:
                q_values = {action: self.q_table[state].get(action, 0) 
                           for action in available_actions}
                action = max(q_values, key=q_values.get)
            else:
                action = random.choice(available_actions)
            
            visited.append(action)
            current = action
        
        return visited