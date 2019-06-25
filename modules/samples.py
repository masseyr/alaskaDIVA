import numpy as np
from common import *
import warnings
from timer import Timer


__all__ = ['Samples']


class Samples(object):
    """
    Class to read and arrange sample data.
    All columns should be data only.
    """

    def __init__(self,
                 samples=None,
                 csv_file=None,
                 names=None):

        """
        :param csv_file: csv file that contains the samples
        :param samples: List of dictionaries
        """
        self.csv_file = csv_file

        self.index = None
        self.nfeat = None

        if samples is not None:
            self.samples = samples
            self.nsamp = len(samples)

        elif csv_file is not None:
            self.samples = Handler(filename=csv_file).read_from_csv(return_dicts=True)
            self.nsamp = len(self.samples)
        else:
            warnings.warn('Empty Samples class initialized')
            self.samples = None
            self.nsamp = 0

        if self.nsamp > 0:
            self.index = list(range(self.nsamp))
        else:
            self.index = list()

        if names is not None:
            self.names = names
        elif self.samples is not None:
            self.names = list(self.samples[0])
        else:
            self.names = list()

        self.nvar = len(self.names)

    def __repr__(self):
        """
        Representation of the Samples object
        :return: Samples class representation
        """
        if self.csv_file is not None:
            return "<Samples object from {cf} with {v} variables, {n} samples>".format(cf=Handler(
                                                                                       self.csv_file).basename,
                                                                                       v=len(self.samples[0]),
                                                                                       n=len(self.samples))
        elif self.csv_file is None and self.samples is not None:
            return "<Samples object with {v} variables, {n} samples>".format(v=len(self.samples[0]),
                                                                             n=len(self.samples))
        else:
            return "<Samples object: __empty__>"

    def merge_data(self,
                   samp):
        """
        Merge two sample sets together
        column and label names and orders should be the same in the two datasets
        :param samp: other samples object
        """
        self.samples = self.samples + samp.samples
        self.nsamp += samp.nsamp
        self.index = list(range(self.nsamp))

    @Timer.timing(True)
    def delete_column(self,
                      column_name=None):
        """
        Function to remove a data column from the samples object
        :param column_name: Column label or name
        :return: None
        """
        if column_name is None:
            raise AttributeError('No argument for delete operation')

        self.samples = list(samp.pop(column_name) for samp in self.samples)

    def extract_column(self,
                       column_name=None):
        """
        Function to extract a data column from the samples object
        :param column_name: Column label or name
        :return: Samples object with only one column
        """

        if column_name is None:
            raise AttributeError('No argument for extract operation')

        return list(samp[column_name] for samp in self.samples)

    def add_column(self,
                   column_name=None,
                   column_data=None):
        """
        Function to add a column to the samples matrix.
        Column_order keyword is used after appending the column name and data to the right of the matrix
        but if column_data is None, self.x is re-ordered according to column_order
        :param column_name: Name of column to be added
        :param column_data: List of column values to be added
        :return: Samples object with added column
        """

        if column_data is None:
            RuntimeError('No argument for add operation')
        if column_name is None:
            col_names = list(self.samples[0])

            added_num_list = list()
            for col_name in col_names:
                if 'added_column' in col_name:
                    added_num_list.append(int(col_name.split('added_column_')[1]))
            if len(added_num_list) > 0:
                added_num_list = list(reversed(sorted(added_num_list)))
            column_name = 'added_column_{}'.format(str(added_num_list[0]+1))
        else:
            column_name = 'added_column_1'

        out_list = list()
        for i, samp in self.samples:
            out_samp = dict()
            for k, v in samp.items():
                out_samp[k] = v
            out_samp[column_name] = column_data[i]
            out_list.append(out_samp)

        self.samples = out_list

    def save_to_file(self,
                     out_file):
        """
        Function to save sample object to csv file
        :param out_file: CSV file full path (string)
        :return: Write to file
        """

        Handler.write_to_csv(self.samples,
                             outfile=out_file,
                             header=True)

    def sample_partition(self,
                         percentage=75):

        """
        Method to randomly partition the samples based on a percentage
        :param percentage: Partition percentage (default: 75)
        (e.g. 75 for 75% training samples and 25% validation samples)
        :return: Tuple (Training sample object, validation sample object)
        """

        ntrn = int((percentage * self.nsamp) / 100.0)

        # randomly select training samples based on number
        trn_sites = np.random.choice(np.array(self.index),
                                     size=ntrn,
                                     replace=False).tolist()
        val_sites = np.array(self.index)[~np.in1d(self.index,
                                         trn_sites)].tolist()

        # training sample object
        trn_samp = Samples(samples=list(self.samples[i] for i in trn_sites))
        trn_samp.names = self.names
        trn_samp.nsamp = len(trn_samp.samples)
        trn_samp.index = list(range(trn_samp.nsamp))
        trn_samp.nfeat = len(trn_samp.samples[0])

        # validation sample object
        val_samp = Samples(samples=list(self.samples[i] for i in val_sites))
        val_samp.names = self.names
        val_samp.nsamp = len(val_samp.samples)
        val_samp.index = list(range(val_samp.nsamp))
        val_samp.nfeat = len(val_samp.samples[0])

        return trn_samp, val_samp

    def random_selection(self,
                         num=None):

        """
        Method to select a smaller number of samples from the Samples object
        :param num: Number of samples to select
        :return: Samples object
        """
        if num is not None:
            if num >= self.nsamp:
                print('Number larger than population: {} specified for {} samples'.format(str(num),
                                                                                          str(self.nsamp)))
                ran_samp_n = self.index
            else:
                ran_samp_n = np.random.choice(self.index,
                                              size=num,
                                              replace=False)

            # training sample object
            ran_samp = Samples(samples=list(self.samples[i] for i in ran_samp_n))
            ran_samp.names = self.names
            ran_samp.nsamp = len(ran_samp.samples)
            ran_samp.index = list(range(ran_samp.nsamp))
            ran_samp.nfeat = len(ran_samp.samples[0])
        else:
            ran_samp = Samples(samples=self.samples)
            ran_samp.names = self.names
            ran_samp.nsamp = self.nsamp
            ran_samp.index = self.index
            ran_samp.nfeat = self.nfeat

        return ran_samp

    def selection(self,
                  index_list):
        """
        Method to select samples based on an index list
        :param index_list:
        :return: Samples object
        """
        if type(index_list).__name__ not in ('list', 'tuple', 'ndarray'):
            raise ValueError('Unsupported index list type')

        if type(index_list).__name__ == 'ndarray':
            index_list = index_list.copy().tolist()

        ran_samp = Samples(samples=list(self.samples[i] for i in index_list))
        ran_samp.names = self.names
        ran_samp.nsamp = len(ran_samp.samples)
        ran_samp.index = list(range(ran_samp.nsamp))
        ran_samp.nfeat = len(ran_samp.samples[0])

        return ran_samp

    def make_folds(self,
                   n_folds=5):

        """
        Make n folds in sample sets
        :param n_folds:
        :return: list of tuples [(training samp, validation samp)...]
        """

        nsamp_list = list(self.nsamp // n_folds for _ in range(n_folds))
        if self.nsamp % n_folds > 0:
            nsamp_list[-1] += self.nsamp % n_folds

        index_list = Opt.__copy__(self.index)
        fold_samples = list()

        for fold_samp in nsamp_list:

            val_index = np.random.choice(index_list,
                                         size=fold_samp,
                                         replace=False)

            trn_index = self.index[~np.in1d(self.index, val_index)]
            index_list = index_list[~np.in1d(index_list, val_index)]

            fold_samples.append((self.selection(trn_index), self.selection(val_index)))

        return fold_samples

    @classmethod
    def get_dict_list(cls,
                      numpy_arr,
                      header):
        """
        Method to convert numpy array to list of dictionaries
        :param numpy_arr:
        :param header:
        :return: list of dicts
        """

        l1 = numpy_arr.tolist()
        out_list = list()

        for list_data in l1:
            out_list.append(dict(zip(header, list_data)))

        return cls(samples=out_list)
