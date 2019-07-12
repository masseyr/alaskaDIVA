import numpy as np
from samples import Samples
from common import Handler, Opt


__all__ = ['Distance',
           'Euclidean']


class Distance(Samples):
    """
    Parent class for all the distance type methods
    """

    def __init__(self,
                 samples=None,
                 csv_file=None,
                 names=None):

        """
        Class constructor
        :param samples: List of sample dictionaries
        :param csv_file: csv file containing samples
        :param names: Name of the data (or coordinate) columns
        :return: Distance object
        """

        super(Distance, self).__init__(samples,
                                       csv_file,
                                       names)

        if self.samples is not None:
            self.matrix = np.array([[Handler.string_to_type(self.samples[i][self.names[j]])
                                     for j in range(0, self.nvar)]
                                    for i in range(0, self.nsamp)])
        else:
            self.matrix = None

        if self.nsamp > 0:
            self.distance_matrix = np.zeros([self.nsamp, self.nsamp],
                                            dtype=np.float)
        else:
            self.distance_matrix = None

    def __repr__(self):
        return "<Distance class object at {}>".format(hex(id(self)))

    def centroid(self,
                 method='median'):
        """
        Method to determine centroid of the sample matrix
        :param method: Type of reducer to use. Options: 'mean', 'median', 'percentile_x'
        :return: Cluster center (vector of column/dimension values)
        """
        if self.matrix is not None:
            if method == 'median':
                return np.array(np.median(self.matrix, axis=0))[0]
            elif method == 'mean':
                return np.array(np.mean(self.matrix, axis=0))[0]
            elif 'percentile' in method:
                perc = int(method.replace('percentile', '')[1:])
                return np.array(np.percentile(self.matrix, perc, axis=0))[0]
            else:
                raise ValueError("Invalid or no reducer")
        else:
            raise ValueError("Sample matrix not found")


class Euclidean(Distance):
    """
    Class for calculating Euclidean distance
    """
    def __init__(self,
                 samples=None,
                 csv_file=None,
                 names=None):
        """
        Class constructor
        :param samples: List of sample dictionaries
        :param csv_file: csv file containing samples
        :param names: Name of the columns or dimensions
        :return: Euclidean distance object
        """

        super(Euclidean, self).__init__(samples,
                                        csv_file,
                                        names)

    def __repr__(self):
        return "<Euclidean class object at {} with {} samples>".format(hex(id(self)),
                                                                       str(len(self.samples)))

    @staticmethod
    def euc_dist(vec1,
                 vec2):
        """
        Method to calculate euclidean distance between two vectors
        :param vec1: first vector
        :param vec2: second vector
        :return: scalar
        """

        return np.linalg.norm(np.array(vec1)-np.array(vec2))

    @staticmethod
    def mat_dist(vec1, mat1):
        """
        Method to calculate euclidean distance between between a vector and all the vectors in a matrix
        :param vec1: vector
        :param mat1: matrix (numpy array of vectors)
        :return: numpy array of scalars
        """
        return np.apply_along_axis(lambda x: Euclidean.euc_dist(x, np.array(vec1)),
                                   1,
                                   mat1)

    def calc_dist_matrix(self,
                         approach=2):
        """
        Method to calculate euclidean distance from each sample
         and make a matrix
        :return: 2d matrix
        """
        if self.distance_matrix is not None:
            Opt.cprint('Building distance matrix : ', newline='')

            if approach == 1:

                self.distance_matrix = np.apply_along_axis(lambda x: Euclidean.mat_dist(x, self.matrix),
                                                           1,
                                                           self.matrix)

            elif approach == 2:
                ndims = self.matrix.shape[1]

                temp_mat = np.zeros([self.matrix.shape[0], self.matrix.shape[0]])

                for dim in range(ndims):
                    arr = np.repeat(self.matrix[:, dim][:, np.newaxis], self.nsamp, 1)
                    arr_ = arr.T
                    temp_mat += (arr - arr_) ** 2

                self.distance_matrix = np.sqrt(temp_mat)

            else:
                raise ValueError('Unrecognized approach')

            Opt.cprint('Done!')

        else:
            raise ValueError('No samples to calculate distances from')

    def proximity_filter(self,
                         thresh=None):
        """
        method to remove points based on proximity threshold
        :param thresh: proximity threshold (default: 90th percentile)
        :return: None
        """
        Opt.cprint('Applying proximity filter...')

        if thresh is None:
            thresh = self.centroid('percentile_90')

        # number of close proximities associated with each element
        n_proxim = np.apply_along_axis(lambda x: np.count_nonzero((x > 0.0) & (x < thresh)),
                                       0,
                                       self.distance_matrix)

        Opt.cprint('Max group size : {} '.format(str(n_proxim.max())), newline='')
        Opt.cprint('Min group size : {} '.format(str(n_proxim.min())))

        # sort the indices in increasing order of n_proxim
        idx = np.argsort(n_proxim).tolist()
        idx_out = list()

        # find indices of elements that should be removed
        for ii in idx:
            if ii not in idx_out:
                arr = self.distance_matrix[ii, 0:(ii+1)]
                temp_list = (np.where((arr < thresh) & (arr > 0.0))[0]).tolist()
                idx_out += temp_list
                idx_out = list(set(idx_out))

        # sort the indices in decreasing order for pop()
        pop_idx = sorted(list(set(idx_out)),
                         reverse=True)

        Opt.cprint('Removing {} elements...'.format(str(len(pop_idx))))

        for pop_id in pop_idx:
            self.samples.pop(pop_id)

        self.nsamp = len(self.samples)


