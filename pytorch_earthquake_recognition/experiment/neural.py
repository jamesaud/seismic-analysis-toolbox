import torch.nn as nn
import torchvision.transforms as transforms


class mnist_model(nn.Module):
    __transformations = transforms.Compose([transforms.Resize((32, 32)),
                                          transforms.ToTensor(),
                                          transforms.Normalize(mean=[0.05744402642343559, 0.013903309317196117, 0.018187494838938993],
                                                               std=[0.0026338661418241613, 0.002147942197089102, 0.00220948527841007])
                                          ])

    transformations = {'train': __transformations, 'test': __transformations}

    def __init__(self):
        super(mnist_model, self).__init__()
        self.feats = nn.Sequential(
            nn.Conv2d(3, 32, 5, 1, 1),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.BatchNorm2d(32),

            nn.Conv2d(32, 64, 3,  1, 1),
            nn.ReLU(True),
            nn.BatchNorm2d(64),

            nn.Conv2d(64, 64, 3,  1, 1),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.BatchNorm2d(64),

            # nn.Conv2d(64, 128, 3, 1, 1),
            # nn.ReLU(True),
            # nn.BatchNorm2d(128)
        )

        self.classifier = nn.Conv2d(64, 3, 1)
        self.avgpool = nn.AvgPool2d(6, 6)
        self.dropout = nn.Dropout(0.5)

    def forward(self, inputs):
        out = self.feats(inputs)
        out = self.dropout(out)
        out = self.classifier(out)
        out = self.avgpool(out)
        out = out.view(-1, 3)
        return out



class reduced_mnist_model(nn.Module):
    __transformations = [transforms.Resize((200, 300)),
                         transforms.RandomCrop((200, 200)),
                         transforms.Grayscale(num_output_channels=3),
                         transforms.Resize((16, 16)),
                         transforms.ToTensor(),
                         transforms.Normalize(mean=[0.05744402642343559, 0.013903309317196117, 0.018187494838938993],
                                             std=[0.0026338661418241613, 0.002147942197089102, 0.00220948527841007])]

    __train = []

    transformations = {'train':  transforms.Compose(__train + __transformations),
                       'test': transforms.Compose(__transformations)
                       }

    def __init__(self):
        super().__init__()
        self.feats = nn.Sequential(
            nn.Conv2d(3, 16, 3, 1, 1),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.BatchNorm2d(16),

            nn.Conv2d(16, 32, 3, 1, 1),
            nn.ReLU(True),
            nn.BatchNorm2d(32),

            nn.Conv2d(32, 32, 5, 1, 1),
            nn.MaxPool2d(2, 2),
            nn.ReLU(True),
            nn.BatchNorm2d(32),

            nn.Conv2d(32, 64, 3,  1, 1),
            nn.ReLU(True),
            nn.BatchNorm2d(64),

        )

        self.classifier = nn.Conv2d(64, 3, 1)
        self.avgpool = nn.AvgPool2d(3, 3)
        self.dropout = nn.Dropout(0.5)

    def forward(self, inputs):
        out = self.feats(inputs)
        out = self.dropout(out)
        out = self.classifier(out)
        out = self.avgpool(out)
        out = out.view(-1, 3)
        return out



class AlexNet(nn.Module):
    regime = [
        {'epoch': 0, 'optimizer': 'SGD', 'lr': 1e-2,
         'weight_decay': 5e-4, 'momentum': 0.9},
        {'epoch': 10, 'lr': 5e-3},
        {'epoch': 15, 'lr': 1e-3, 'weight_decay': 0},
        {'epoch': 20, 'lr': 5e-4},
        {'epoch': 25, 'lr': 1e-4}
    ]
    normalize = transforms.Normalize(mean=[0.05744402642343559, 0.013903309317196117, 0.018187494838938993],
                                     std=[0.002633864739361931, 0.0021479396259083466, 0.002209487849590825])
    transformations = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),  # 256
            transforms.ToTensor(),
            normalize
        ]),
        'test': transforms.Compose([
            transforms.Resize((224, 224)),   # 256
            transforms.ToTensor(),
            normalize
        ])
    }

    def __init__(self, num_classes=3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2,
                      bias=False),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 192, kernel_size=5, padding=2, bias=False),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(192),
            nn.Conv2d(192, 384, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(384),
            nn.Conv2d(384, 256, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(256),
            nn.Conv2d(256, 256, kernel_size=3, padding=1, bias=False),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(256)
        )
        self.classifier = nn.Sequential(
            nn.Linear(256 * 6 * 6, 4096, bias=False),
            nn.BatchNorm1d(4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096, bias=False),
            nn.BatchNorm1d(4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, num_classes)
        )


    def forward(self, x):
        x = self.features(x)
        x = x.view(-1, 256 * 6 * 6)
        x = self.classifier(x)
        return x


