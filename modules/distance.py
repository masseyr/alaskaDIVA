import numpy as np
from samples import Samples
from common import Handler


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

    def calc_dist_matrix(self):
        """
        Method to calculate euclidean distance from each sample
         and make a matrix
        :return: 2d matrix
        """
        if self.distance_matrix is not None:

            for ii in range(self.nsamp):
                self.distance_matrix[:, ii] = np.apply_along_axis(lambda x: Euclidean.euc_dist(x, self.matrix[ii, :]),
                                                                  1,
                                                                  self.matrix)

        else:
            raise ValueError('No samples to calculate distances from')

    def proximity_filter(self,
                         thresh=None):
        """
        method to remove points based on proximity threshold
        :param thresh: proximity threshold (default: 90th percentile)
        :return: None
        """

        if thresh is None:
            thresh = self.centroid('percentile_90')

        n_proxim = np.apply_along_axis(lambda x: np.count_nonzero(x < thresh),
                                       0,
                                       self.distance_matrix)

        idx = np.argsort(n_proxim).tolist()
        idx_out = list()

        for ii in idx:
            for jj in range(ii+1):
                if ii not in idx_out:
                    if self.distance_matrix[ii, jj] < thresh:
                        if ii != jj:
                            idx_out.append(jj)

        pop_idx = sorted(np.unique(idx_out).tolist(),
                         reverse=True)

        for pop_id in pop_idx:
            self.samples.pop(pop_id)

        self.nsamp = len(self.samples)


