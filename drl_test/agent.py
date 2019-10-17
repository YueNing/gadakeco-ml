from replaybuffer import ReplayBuffer
from network import Network
from typing import List, Dict, Tuple
import torch
import torch.optim as optim
import gym
import numpy as np 
import torch.nn.functional as F 
import matplotlib.pyplot as plt

class DQNAgent:
    """ simple dqn agent """
    def __init__(
        self,
        env: gym.Env,
        memory_size: int,
        batch_size: int,
        target_update: int,
        epsilon_decay: float,
        max_epsilon: float = 1.0,
        min_epsilon: float = 0.1,
        gamma: float = 0.99,
    ):
        obs_dim = env.observation_space.shape[0]
        action_dim = env.action_space.n 

        self.env = env 
        self.memory = ReplayBuffer(obs_dim, memory_size, batch_size)
        self.batch_size = batch_size
        self.epsilon = max_epsilon
        self.epsilon_decay = epsilon_decay
        self.max_epsilon = max_epsilon
        self.min_epsilon = min_epsilon
        self.target_update = target_update
        self.gamma = gamma

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)

        # network, dqn used as trained and updated, dqn_target set to eval mode
        self.dqn = Network(obs_dim, action_dim).to(self.device)
        self.dqn_target = Network(obs_dim, action_dim).to(self.device)
        self.dqn_target.load_state_dict(self.dqn.state_dict())
        self.dqn_target.eval()

        # optimizer
        self.optimizer = optim.Adam(self.dqn.parameters())

        # transition to store in memory
        self.transistion = List()

        # mode: train / test
        self.is_test = False

    def select_action(
        self,
        state: np.ndarray
    )-> np.ndarray:

        """select an action from the input state"""

        if self.epsilon > np.random.random():
            selected_action = self.env.action_space.sample()
        else:
            # nn.module __call__ function
            selected_action = self.dqn(
                    torch.FloatTensor(state).to(self.device)
                ).argmax()
            selected_action = selected_action.detach().cpu().numpy()
        
        if not self.is_test:
            self.transistion = [state, selected_action]
        
        return selected_action
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, np.float64, bool]:
        next_state, reward, done, _ = self.env.step(action)

        if not self.is_test:
            self.transistion += [reward, next_state, done]
            self.memory.store(*self.transistion)
        return next_state, reward, done
    
    def _compute_dqn_loss(
        self,
        samples: Dict[str, np.ndarray]
    ) -> torch.Tensor:
        device = self.device
        state = torch.FloatTensor(samples["obs"]).to(device)
        next_state = torch.FloatTensor(samples["next_obs"]).to(device)
        action = torch.LongTensor(samples["acts"].reshape(-1, 1)).to(device)
        reward = torch.FloatTensor(samples["rews"].reshape(-1, 1)).to(device)
        done = torch.FloatTensor(samples["done"].reshape(-1, 1)).to(device)

        curr_q_value = self.dqn(state).gather(1, action)
        next_q_value = self.dqn_target(
            next_state
        ).max(dim=1, keepdim=True)[0].detach()
        mask = 1 - done
        target = (reward + self.gamma * next_q_value * mask).to(self.device)

        # calculate dqn loss
        loss = F.smooth_l1_loss(curr_q_value, target)
        
        return loss

    def update_model(self) -> torch.Tensor:
        samples = self.memory.sample_batch()
        loss = self._compute_dqn_loss(samples)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def _target_hard_update(self):
        self.dqn_target.load_state_dict(self.dqn.state_dict())
    
    def _plot(
        self,
        frame_idx: int,
        scores: List[float],
        losses: List[float],
        epsilons: List[float],
    ):
    
        plt.figure(figsize=(20, 5))
        plt.subplot(131)
        plt.title('frame %s. score: %s' % (frame_idx, np.mean(scores[-10:])))
        plt.plot(scores)
        plt.subplot(132)
        plt.title('loss')
        plt.plot(losses)
        plt.subplot(133)
        plt.title('epsilons')
        plt.plot(epsilons)
        plt.show()
    
    def train(
        self,
        num_frames: int,
        plotting_interval: int=200,
    ):
        self.is_test = False
        
        state = self.env.reset()
        update_cnt = 0
        epsilons = []
        losses = []
        scores = []
        scre = 0

        for frame_idx in range(1, num_frames + 1):
            action = self.select_action(state)
            next_state, reward, done = self.step(action)

            state = next_state
            score += reward

            if done:
                state = self.env.reset()
                scores.append(score)
                score = 0

            # if training is ready
            if len(self.memory) >= self.batch_size:
                loss = self.update_model()
                losses.append(loss)
                update_cnt +=1

                self.epsilon = max(self.min_epsilon, self.epsilon-(self.max_epsilon-self.min_epsilon) * self.epsilon_decay)
                epsilons.append(self.epsilon)

                if update_cnt % self.target_update == 0:
                    self._target_hard_update()
                
            if frame_idx % plotting_interval == 0:
                self._plot(frame_idx, scores, losses, epsilons)
            
        self.env.close()



class DDQNAgent:
    pass
