import torch
from torch import nn
import torch.nn.functional as F

def off_diagonal(x):
    # return a flattened view of the off-diagonal elements of a square matrix
    n, m = x.shape
    assert n == m
    return x.flatten()[:-1].view(n - 1, n + 1)[:, 1:].flatten()

class GeM(nn.Module):
    '''
    Code modified from the 2d code in
    https://amaarora.github.io/2020/08/30/gempool.html
    '''
    def __init__(self, kernel_size=8, p=3, eps=1e-6):
        super(GeM,self).__init__()
        self.p = nn.Parameter(torch.ones(1)*p)
        self.kernel_size = kernel_size
        self.eps = eps

    def forward(self, x):
        return self.gem(x, p=self.p, eps=self.eps)
        
    def gem(self, x, p=3, eps=1e-6):
        return F.avg_pool1d(x.clamp(min=eps).pow(p), self.kernel_size).pow(1./p)
        
    def __repr__(self):
        return self.__class__.__name__ + \
                '(' + 'p=' + '{:.4f}'.format(self.p.data.tolist()[0]) + \
                ', ' + 'eps=' + str(self.eps) + ')'
                

"""class CNN1d(nn.Module):
    # inspired by https://www.kaggle.com/scaomath/g2net-1d-cnn-gem-pool-pytorch-train-inference
    def __init__(self):
        super().__init__()
        
        self.cnn1 = nn.Sequential(
            nn.Conv1d(1, 64, kernel_size=64),
            nn.BatchNorm1d(64),
            nn.SiLU(),
        )
        self.cnn2 = nn.Sequential(
            nn.Conv1d(64, 64, kernel_size=32),
            GeM(kernel_size=2),
            nn.BatchNorm1d(64),
            nn.SiLU(),
        )
        
        self.cnn3 = nn.Sequential(
            nn.Conv1d(64, 64, kernel_size=32),
            nn.BatchNorm1d(64),
            nn.SiLU(),
        )
        
        self.t1 = nn.Sequential(
            nn.Conv1d(64, 64, kernel_size=32),
            GeM(kernel_size=4),
            nn.BatchNorm1d(64),
            nn.SiLU(),            
            nn.Conv1d(64, 128, kernel_size=32),
            nn.BatchNorm1d(128),
            nn.SiLU(),
        )
            
        self.cnn4 = nn.Sequential(
            nn.Conv1d(128, 128, kernel_size=16),
            GeM(kernel_size=6),
            nn.BatchNorm1d(128),
            nn.SiLU(),
        )
        

        self.cnn5 = nn.Sequential(
            nn.Conv1d(128, 256, kernel_size=16),
            nn.BatchNorm1d(256),
        )
        
        self.gru = nn.GRU(256, 128, bidirectional=True,
                          batch_first=True)
        
        self.cnn6 = nn.Sequential(
            nn.Conv1d(256, 256, kernel_size=16),
            GeM(kernel_size=4),
            nn.BatchNorm1d(256),
            nn.SiLU(),
        )

        self.cnn7 = nn.Sequential(
            nn.Conv1d(256, 256, kernel_size=1),
            nn.BatchNorm1d(256),
            nn.SiLU(),
        )

        self.fc = nn.Linear(256*10, 2048)

    def forward(self, x):
        x = self.cnn1(x)
        x = self.cnn2(x)
        x = self.cnn3(x)
        x = self.t1(x)
        x = self.cnn4(x)
        x = self.cnn5(x)
        x = self.gru(x.transpose(2, 1))[0].transpose(2, 1)
        x = self.cnn6(x)
        x = self.cnn7(x)
        x = x.flatten(start_dim=1)
        x = self.fc(x)
        return x"""
class CNN1d(nn.Module):
    def __init__(self):
        super(DeepFeatureNet, self).__init__()

        self.use_dropout = use_dropout
        
        # Convolutional layers with small filter size
        self.conv1_stream1 = self._conv1d_layer(input_dims, 64, filter_size=50, stride=6)
        self.pool1_stream1 = nn.MaxPool1d(kernel_size=8, stride=8)
        self.conv2_stream1 = self._conv1d_layer(64, 128, filter_size=8, stride=1)
        self.conv3_stream1 = self._conv1d_layer(128, 64, filter_size=8, stride=1)
        self.conv4_stream1 = self._conv1d_layer(64, 32, filter_size=8, stride=1)
        self.pool2_stream1 = nn.MaxPool1d(kernel_size=4, stride=4)

        # Convolutional layers with large filter size
        self.conv1_stream2 = self._conv1d_layer(input_dims, 64, filter_size=200, stride=25)
        self.pool1_stream2 = nn.MaxPool1d(kernel_size=4, stride=4)
        self.conv2_stream2 = self._conv1d_layer(64, 128, filter_size=6, stride=1)
        self.conv3_stream2 = self._conv1d_layer(128, 64, filter_size=6, stride=1)
        self.conv4_stream2 = self._conv1d_layer(64, 32, filter_size=6, stride=1)
        self.pool2_stream2 = nn.MaxPool1d(kernel_size=2, stride=2)
        self.dropout=nn.Dropout(0.5)
        # Final layers
        self.fc_concat = nn.Linear(512, 256)
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, n_classes)
    def _conv1d_layer(self, in_channels, out_channels, filter_size, stride):
        return nn.Sequential(
            nn.Conv1d(in_channels, out_channels, kernel_size=filter_size, stride=stride),
            nn.BatchNorm1d(out_channels),
            nn.ReLU()
        )
        
    def forward(self, x):
        # Stream 1
        out1_stream1 = self.conv1_stream1(x)
        out1_stream1 = self.pool1_stream1(out1_stream1)
        out1_stream1 = self.dropout(out1_stream1)#self._apply_dropout(out1_stream1)
        out1_stream1 = self.conv2_stream1(out1_stream1)
        out1_stream1 = self.conv3_stream1(out1_stream1)
        out1_stream1 = self.conv4_stream1(out1_stream1)
        out1_stream1 = self.pool2_stream1(out1_stream1)
        # Stream 2
        out1_stream2 = self.conv1_stream2(x)
        out1_stream2 = self.pool1_stream2(out1_stream2)
        out1_stream2 = self.dropout(out1_stream2)#self._apply_dropout(out1_stream2)
        out1_stream2 = self.conv2_stream2(out1_stream2)
        out1_stream2 = self.conv3_stream2(out1_stream2)
        out1_stream2 = self.conv4_stream2(out1_stream2)
        out1_stream2 = self.pool2_stream2(out1_stream2)

        # Concatenate streams
        concatenated = torch.cat((out1_stream1, out1_stream2), dim=2)
        # Flatten
        flattened = concatenated.view(concatenated.size(0), -1)
        # Final fully connected layer
        output = self.fc_concat(flattened)
       # output=self._apply_dropout(output)
        """output=self.dropout(output)
        output=self.fc1(output)
        output=self.dropout(output)
        output=self.fc2(output)"""     
        return output
        
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.cnn1 = CNN1d()
        self.cnn2 = CNN1d()

        sizes = [256] + [3192] * 3
        # projector
        layers = []
        for i in range(len(sizes) - 2):
            layers.append(nn.Linear(sizes[i], sizes[i + 1], bias=False))
            layers.append(nn.BatchNorm1d(sizes[i + 1]))
            layers.append(nn.ReLU(inplace=True))
        layers.append(nn.Linear(sizes[-2], sizes[-1], bias=False))
        self.projector = nn.Sequential(*layers)
        self.lambd = 0.0051
        # normalization layer for the representations z1 and z2
        self.bn = nn.BatchNorm1d(sizes[-1], affine=False)

    def forward(self, x, label=None, mode='train'):
        if mode != 'train':
            z1 = self.cnn1(x[:, 0:1])
            z2 = self.cnn1(x[:, 1:2])
            z3 = self.cnn2(x[:, 2:3])
            return z1, z2, z3
        
        z1 = self.projector(self.cnn1(x[:, 0:1]))
        z2 = self.projector(self.cnn2(x[:, 1:2]))
        # empirical cross-correlation matrix
        c = self.bn(z1).T @ self.bn(z2)

        # sum the cross-correlation matrix between all gpus
        c.div_(z1.shape[0])

        on_diag = torch.diagonal(c).add_(-1).pow_(2).sum()
        off_diag = off_diagonal(c).pow_(2).sum()
        loss = on_diag + self.lambd * off_diag
        return loss
    
    
class NetEval(nn.Module):
    def __init__(self, weight_paths,
                 mode='train'):
        super(NetEval, self).__init__()
        self.backbone = Net()
        if mode=='train':
            from utils import average_model
            averaged_w = average_model(weight_paths)
            self.backbone.load_state_dict(averaged_w)
            del averaged_w
        self.backbone.eval()
        self.fc = nn.Linear(2048*3, 1)
        
    def forward(self, x, mode='val'):
        with torch.no_grad():
            z1, z2, z3 = self.backbone(x, mode='val')
        return self.fc(torch.cat([z1, z2, z3], -1))

            
if __name__ == "__main__":
    bsz = 16
    x = torch.randn(bsz, 3, 4096)
    y = torch.zeros((bsz,))
    model = Net()
    loss = model(x)
    print(loss)
    z1, z2, z3 = model(x, mode='val')
    print(z1.shape)

    model = NetEval(None, mode='val')
    pred = model(x)
    print(pred.shape)
