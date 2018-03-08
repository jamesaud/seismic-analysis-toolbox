from PIL import Image
from torch.utils.data.dataset import Dataset
from torchvision import transforms
import glob
from matplotlib import pyplot as plt
from random import shuffle

IMG_PATH = './spectrograms/'
IMG_EXT = '.png'

class SpectrogramDataset(Dataset):
    """
    """

    def __init__(self, img_path, transform=None, test=False, test_sample_every=7):   # about 15%
        self.img_path = img_path
        self.transform = transform
        all_file_paths = glob.glob('./spectrograms/**/HNZ.png', recursive=True)

        self.train_file_paths = []
        self.test_file_paths = []
        for i, path in enumerate(all_file_paths):
            if (i % test_sample_every == 0):
                self.test_file_paths.append(path)
            else:
                self.train_file_paths.append(path)

        self.file_paths = self.test_file_paths if test else self.train_file_paths
        shuffle(self.file_paths)

        self.labels = {
            'noise': 0,
            'local': 1,
            'non_local': 2
        }
        self.reverse_map(self.labels)

    @staticmethod
    def reverse_map(dic):
        dic.update({v:k for k,v in dic.items()})

    def __getitem__(self, index):
        path = self.file_paths[index]
        img = Image.open(path)
        img = img.convert('RGB')

        if self.transform:
            img = self.transform(img)

        label = self.label_to_number(self.get_label(path))
        return img, label

    def __len__(self):
        return len(self.file_paths)


    @staticmethod
    def get_label(file_path):
        return file_path.split('/')[-3]


    def label_to_number(self, label):
        return self.labels[label]

    def number_to_label(self, label):
        return


    @staticmethod
    def show_img(image):
        plt.imshow(image)
        plt.pause(0.001)


    @classmethod
    def preview_dataset(cls, number=3):
        dataset = cls(IMG_PATH)

        fig = plt.figure()

        for i in range(number):
            sample, label = dataset[i]
            ax = plt.subplot(1, number, i + 1)
            plt.tight_layout()
            ax.set_title('Sample #{}'.format(i))
            ax.axis('off')
            cls.show_img(sample)

        plt.show()

    @classmethod
    def preview_image(cls, image):
        plt.tight_layout()
        cls.show_img(image)
        plt.show()

if __name__ == '__main__':
    transformations = transforms.Compose([transforms.Resize(32), transforms.ToTensor()])
    dataset_train = SpectrogramDataset(IMG_PATH, transform=transformations)
    dataset_train.preview_dataset()