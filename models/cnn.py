import torch
from torch.nn import functional as F
from torch import nn
from pytorch_lightning.core.lightning import LightningModule


from torch.optim import Adam
import torchmetrics

class CNN(LightningModule):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(1, 32, 3)
        self.pool = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 32, 3)
        self.fc1 = nn.Linear(32 * 14 * 30, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 8)

        self.accuracy = torchmetrics.Accuracy()
        self.confusion = torchmetrics.ConfusionMatrix(num_classes=8)

    def forward(self, x):
        batch_size,  height, width = x.size()

        x = x.view(batch_size, 1 , height , width)

        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        # print("sahpe",x.shape)
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)

        self.accuracy(logits, y)
        self.log('train_acc_step', self.accuracy, prog_bar=True)

        return loss

    def training_epoch_end(self, outs):
        self.log('train_acc_epoch', self.accuracy)

    def configure_optimizers(self):
        return Adam(self.parameters(), lr=1e-3)
