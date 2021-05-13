import numpy as np


def sn_random_numbers(shape, antithetic=True, moment_matching=True,
                      fixed_seed=False):
    """ Returns an array of shape shape with (pseudo) random numbers
    that are standard normally distributed. """
    if fixed_seed:
        np.random.seed(42)
    if antithetic:
        random_dist = np.random.standard_normal((shape[0], shape[1], int(shape[2] / 2)))
        random_dist = np.concatenate((random_dist, -random_dist), axis=2)
    else:
        random_dist = np.random.standard_normal(shape)
    if moment_matching:
        random_dist = random_dist - np.mean(random_dist)
        random_dist = random_dist / np.std(random_dist)
    if shape[0] == 1:
        return random_dist[0]
    else:
        return random_dist
