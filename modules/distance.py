import numpy as np


__all__ = ['Distance',
           'Euclidean']


class Distance(object):
    """
    Parent class for all the distance type methods
    """

    def __init__(self,
                 samples=None,
                 names=None):
        """
        Class constructor
        :param samples: List of sample dictionaries
        :param names: Name of the data (or coordinate) columns
        :return: Distance object
        """
        self.samples = samples
        self.nsamp = len(samples)
        self.nvar = len(self.names)
        self.names = names
        self.index = list(range(0, self.nsamp))

        self.matrix = np.matrix([[self.samples[i][self.names[j]]
                                  for j in range(0, self.nvar)]
                                 for i in range(0, self.nsamp)])

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
                 names=None):
        """
        Class constructor
        :param samples: List of sample dictionaries
        :param names: Name of the columns or dimensions
        :return: Euclidean distance object
        """

        super(Euclidean, self).__init__(samples,
                                        names)

        self.distance_matrix = None

    def __repr__(self):
        return "<Euclidean class object at {}>".format(hex(id(self)))

    @staticmethod
    def vec_dist(vec1,
                 vec2):
        """
        Method to calculate distance between two vectors
        :param vec1: first vector
        :param vec2: second vector
        :return: scalar
        """
        return np.linalg.norm(np.array(vec1)-np.array(vec2))

    def calc_dist_matrix(self):
        """
        Method to calculate euclidean distance from scene center
        :return: 2d matrix
        """
        out_stack = None

        for ii in range(self.nvar):
            temp_tile = np.tile(self.matrix[:, ii][:, np.newaxis], (1, self.nsamp))[np.newaxis]

            if ii == 0:
                out_stack = temp_tile
            else:
                out_stack = np.vstack([out_stack, temp_tile])

        for jj in range(self.nvar):
            temp_tile = np.tile(self.matrix[:, jj][:, np.newaxis], (1, self.nsamp))[np.newaxis].T

            out_stack = np.vstack([out_stack, temp_tile])

        self.distance_matrix = np.apply_along_axis(lambda x: np.linalg.norm(x[:self.nvar]-x[self.nvar:]),
                                                   0,
                                                   out_stack)

    def proximity_filter(self,
                         thresh=None):
        """
        method to remove points based on proximity threshold
        :param thresh: proximity threshold (default: 90th percentile)
        :return: None
        """

        if thresh is None:
            thresh = self.centroid('percentile_90')

        bad_loc = np.where(self.distance_matrix > thresh)

        uniq, index, count = np.unique(np.concatenate(bad_loc),
                                       return_index=True,
                                       return_counts=True)

        bad_pts1 = uniq[np.where(count > 2)[0]]

        bad_pts2_loc = index[np.where(count == 2)[0]]
        bad_pts2_arr = np.array([bad_loc[0][bad_pts2_loc], bad_loc[1][bad_pts2_loc]])
        bad_pts2_tup_list = list(tuple(bad_pts2_arr[:, i]) for i in range(bad_pts2_arr.shape[1]))

        bad_pts2 = list()
        for bad_pts2_tup in bad_pts2_tup_list:
            if bad_pts2_tup[0] in bad_pts2:
                continue
            else:
                bad_pts2.append(bad_pts2_tup[1])

        bad_pts2 = np.array(bad_pts2)

        bad_pts = np.concatenate([bad_pts1, bad_pts2])

        good_pts_list = np.delete(np.array(range(self.nsamp)), bad_pts).tolist()

        self.samples = list(self.samples[i] for i in good_pts_list)
