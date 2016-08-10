""" An example highlighting the difference between DMD and streaming DMD

    Streaming DMD is a modification of the "standard" DMD procedure that
    produces *APPROXIMATIONS* of the DMD modes and eigenvalues.  The benefit
    of this procedure is that it can be applied to data sets with large
    (in theory, infinite) numbers of snapshots provided the underlying
    system is effectively low-rank.

    Returns
    -------
    Outputs a plot comparing the streaming and standard eigenvalues
"""

import sys
sys.path.append('..')

import dmdtools
import numpy as np
import matplotlib.pyplot as plt

max_rank = 0   # maximum allowable rank of the DMD operator (0 = unlimited)
n_snaps = 501                   # total number of snapshots to be processed
n_states = 4000                 # number of states
noise_cov = 1.e-4               # measurement noise covariance

dt = 0.01                       # timestep

np.random.seed(0)


def snapshots(n_states, n_snaps, noise_cov=0):
    # Define the example system
    v1 = np.random.randn(n_states)
    v2 = np.random.randn(n_states)
    v3 = np.random.randn(n_states)
    v4 = np.random.randn(n_states)
    # characteristic frequencies
    f1 = 5.2
    f2 = 1.0
    for k in range(n_snaps):
        x = (v1 * np.cos(2 * np.pi * f1 * dt * k) +
             v2 * np.cos(2 * np.pi * f2 * dt * k) +
             v3 * np.sin(2 * np.pi * f1 * dt * k) +
             v4 * np.sin(2 * np.pi * f2 * dt * k))
        yield x + np.sqrt(noise_cov) * np.random.randn(n_states)


def standard_dmd():
    X = np.zeros((n_states, n_snaps-1))
    Y = np.zeros((n_states, n_snaps-1))
    snaps = snapshots(n_states, n_snaps, noise_cov)
    x = snaps.next()
    for k, y in enumerate(snaps):
        X[:, k] = x
        Y[:, k] = y
        x = y

    DMD = dmdtools.DMD()
    DMD.fit(X, Y)
    return DMD.modes, DMD.evals


def streaming_dmd():
    sdmd = dmdtools.StreamingDMD(max_rank)
    snaps = snapshots(n_states, n_snaps, noise_cov)
    x = snaps.next()
    for y in snaps:
        sdmd.update(x, y)
        x = y
    return sdmd.compute_modes()


def main(streaming):
    modes, evals = streaming_dmd() if streaming else standard_dmd()
    fdmd = np.abs(np.angle(evals)) / (2 * np.pi * dt)
    n_modes = len(fdmd)
    ydmd = np.zeros(n_modes)
    for i in range(n_modes):
        ydmd[i] = np.linalg.norm(modes[:, i] * np.abs(evals[i]))
    ydmd /= max(ydmd)
    plt.stem(fdmd, ydmd)
    plt.show()


def compare_methods():
    np.random.seed(0)
    modes, evals = standard_dmd()

    np.random.seed(0)
    modes2, evals2 = streaming_dmd()

    evals.sort()
    evals2.sort()
    # print("standard:")
    # print(evals)
    # print("\nstreaming:")
    # print(evals2)
    plt.plot(evals.real, evals.imag, 'x')
    plt.plot(evals2.real, evals2.imag, '+')
    plt.legend(["DMD", "Streaming"])
    plt.title("DMD Spectrum")
    plt.xlabel(r"$\Re(\lambda)$")
    plt.ylabel(r"$\Im(\lambda)$")
    plt.show()

    print(np.allclose(evals, evals2))

if __name__ == "__main__":
    streaming = True
    #main(streaming)
    compare_methods()
