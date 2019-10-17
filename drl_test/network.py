import torch
import torch.nn as nn
import torch.nn.functional as F 
import torch.optim as optim 

class Network(nn.Module):
    def __init__(self, in_dim:int, out_dim:int):
        super(Network, self).__init__()

        self.layers = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLu(),
            nn.Linear(128, 128),
            nn.ReLu(),
            nn.Linear(128, out_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)