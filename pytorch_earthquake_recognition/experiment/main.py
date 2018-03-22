import torch
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from torchvision import transforms
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader
from torchvision import transforms
from custom_loader import SpectrogramDataset
import torchvision
from neural import mnist_model
import numpy as np

IMG_PATH = './spectrograms/'
IMG_EXT = '.png'
BATCH_SIZE = 4


transformations = transforms.Compose([transforms.Resize((32, 32)),
                                      transforms.ToTensor(),
                                      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
                                      ])

# Dataset
dataset_train = SpectrogramDataset(IMG_PATH, transform=transformations)
dataset_test = SpectrogramDataset(IMG_PATH, transform=transformations)

# Sampler
indices = list(range(len(dataset_train)))
np.random.shuffle(indices)
test_split = 200

train_idx, test_idx = indices[test_split:], indices[:test_split]

train_sampler = SubsetRandomSampler(train_idx)
test_sampler = SubsetRandomSampler(test_idx)

# Data Loader
train_loader = DataLoader(dataset_train,
                          batch_size=BATCH_SIZE,
                          sampler=train_sampler,
                          num_workers=2 # 1 for CUDA
                         # pin_memory=True # CUDA only
                         )

test_loader = DataLoader(dataset_test,
                          batch_size=BATCH_SIZE,
                          sampler=test_sampler,
                          num_workers=2 # 1 for CUDA
                         # pin_memory=True # CUDA only
                         )

# Setup Net
net = mnist_model()
optimizer =  optim.Adam(net.parameters(), lr=0.01) # optim.SGD(net.parameters(), lr=0.01, momentum=0.5)
criterion = nn.CrossEntropyLoss()


# Train and test
def train(epoch):
    running_loss = 0.0
    for i, (inputs, labels) in enumerate(train_loader, 0):

        # wrap them in Variable
        inputs, labels = Variable(inputs), Variable(labels)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)

        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.data[0]

        def print_loss():
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, i * len(inputs), len(train_loader.dataset),
                       100. * i / len(train_loader), loss.data[0]))

        if i % (1000 / BATCH_SIZE) == 0:
            print_loss()

def test():
    correct = 0
    total = 0
    for data in test_loader:
        images, labels = data
        outputs = net(Variable(images))
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum()

    print('Accuracy of the network on the test images: %d %%' % (100 * correct / total))


def guess_labels(batches):
    dataiter = iter(test_loader)

    for i in range(batches):
        images, labels = dataiter.next()

        # print images
        print('GroundTruth: ', ' '.join('%5s' % labels[j] for j in range(4)))

        outputs = net(Variable(images))

        _, predicted = torch.max(outputs.data, 1)

        print('Predicted:   ', ' '.join('%5s' % predicted[j] for j in range(4)))
        print()


def class_evalutation():
    class_correct = list(0 for i in range(3))
    class_total = list(0 for i in range(3))
    for data in test_loader:
        images, labels = data
        outputs = net(Variable(images))
        _, predicted = torch.max(outputs.data, 1)
        c = (predicted == labels).squeeze()
        for i in range(3):
            label = i
            try:
                class_correct[label] += c[i]
                class_total[label] += 1
            except IndexError:
                continue

    for i in range(3):
        print('Accuracy of %5s : %2d %%' % (
            i, 100 * class_correct[i] / class_total[i]))


def save_model(path):
    torch.save(net.state_dict(), path)


def load_model(path):
    return net.load_state_dict(torch.load(path))


if __name__ == '__main__':
    path = './models/model1.pt'

    # for epoch in range(10):
    #       train(epoch)
    # test()
    # save_model(path)

    #######################

    # load_model(path)
    # test()
    #
    # class_evalutation()
    # guess_labels(1)

    print(torch.cuda.is_available())