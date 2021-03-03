from torch.utils.data import Dataset, DataLoader
import glob
import soundfile
from argparse import ArgumentParser
import random
import h5py
import numpy as np

class DataProvider(object):

    @staticmethod
    def add_data_provider_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)

        parser.add_argument('--train_data_root', type=str, default='data/samples/')
        parser.add_argument('--valid_data_root', type=str, default='data/eval_segments')
        parser.add_argument('--meta_data_root', type=str, default='meta_data')
        return parser

    def __init__(self, train_data_root, valid_data_root, meta_data_root, batch_size, num_workers, pin_memory):
        self.train_data_root = train_data_root
        self.valid_data_root = valid_data_root
        self.meta_data_root = meta_data_root
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory

    def get_training_dataset_and_loader(self):
        training_set = AudiosetDoubleLoader(self.train_data_root, self.meta_data_root, data_num=99999)

        loader = DataLoader(training_set, shuffle=True, batch_size=self.batch_size,
                            num_workers=self.num_workers,
                            pin_memory=self.pin_memory)

        return training_set, loader

    def get_validation_dataset_and_loader(self):
        validation_set = AudiosetDoubleLoader(self.valid_data_root, self.meta_data_root, data_num=99999)

        loader = DataLoader(validation_set, shuffle=False, batch_size=self.batch_size,
                            num_workers=self.num_workers,
                            pin_memory=self.pin_memory)

        return validation_set, loader


class AudiosetDataset(Dataset):
    """
        Audioset
    """
    def __init__(self,
                 data_root='data/samples',
                 meta_root='meta_data',
                 data_num=99999
                 ):
        """
        :param data_root:
        :param meta_root:
        :param data_num:
        """

        super(AudiosetDataset, self).__init__()
        self.data_root = data_root
        self.meta_root = meta_root

        # file list
        self.files = glob.glob(f'{self.data_root}/*.wav')
        self.label2num, self.label2class = self.labels_indices(meta_root = self.meta_root)
        self.num = min(len(self.files), data_num) # limit number of loaded

    def __len__(self):
        return self.num

    def __getitem__(self, idx):
        """

        :param idx:
        :return: (audio, label_names)
            audio : ndarray of wavfiles
            class_names : list of label names
        """
        # audio file
        arg_dicts = {
            'file': self.files[idx],
            'dtype': 'float32',
        }
        audio = soundfile.read(**arg_dicts)[0]

        # class file
        class_file = self.files[idx].replace('wav','txt')
        with open(class_file, 'r', encoding='utf8') as f:
            labels = f.readline().split(',')
        names = [self.label2class[label.replace(' ','')] for label in labels]

        return audio, names

    def labels_indices(self, meta_root):
        label2num = {}
        label2class = {}
        with open(f'{meta_root}/class_labels_indices.csv', 'r', encoding='utf8') as f:
            indexes = f.readline()
            for line in f.readlines():
                splited = line.replace('\n', '').split(',')
                num = int(splited[0].replace(' ',''))
                label = splited[1].replace(' ','')
                classes = splited[2].replace(' ', '_').replace('\"','')

                label2num[label] = num
                label2class[label] = classes

        return label2num, label2class


class AudiosetDoubleLoader(AudiosetDataset):
    """
        Audioset
    """
    def __init__(self,
                 data_root='data/samples',
                 meta_root='meta_data',
                 data_num=99999):
        super(AudiosetDoubleLoader, self).__init__(data_root, meta_root, data_num)

    def __getitem__(self, idx):
        """

        :param idx:
        :return: (audio, label_names)
            audio : ndarray of wavfiles
            class_names : list of label names
        """

        # first
        ## audio file
        arg_dicts = {
            'file': self.files[idx],
            'dtype': 'float32',
        }
        audio1 = soundfile.read(**arg_dicts)[0]

        ## class file
        class_file = self.files[idx].replace('wav', 'txt')
        with open(class_file, 'r', encoding='utf8') as f:
            labels = f.readline().split(',')
        names1 = [self.label2class[label.replace(' ', '')] for label in labels]

        # second
        idx2 = (random.randint(1, self.num) + idx) % self.num
        ## second audio file
        arg_dicts = {
            'file': self.files[idx2],
            'dtype': 'float32',
        }
        audio2 = soundfile.read(**arg_dicts)[0]

        ## second class file
        class_file = self.files[idx2].replace('wav', 'txt')
        with open(class_file, 'r', encoding='utf8') as f:
            labels = f.readline().split(',')
        names2 = [self.label2class[label.replace(' ', '')] for label in labels]

        return (audio1, names1), (audio2, names2)



if __name__ == '__main__':
    train_data_root = 'data/samples'
    valid_data_root = 'data/eval_segments'
    meta_data_root = 'meta_data'
    batch_size = 64
    num_workers = 0
    pin_memory = True
    data = DataProvider(train_data_root, valid_data_root, meta_data_root, batch_size,
                        num_workers, pin_memory)

    trainset, trainloader = data.get_training_dataset_and_loader()
    validset, validloaer = data.get_validation_dataset_and_loader()

    (a1, n1), (a2, n2) = validset[0]