import numpy as np
import math
import control.matlab as ml
import matplotlib.pyplot as plt


def drawtf(numerator, denominator):
    num, den = numerator, denominator

    G = ml.tf(num, den)

    print(G, ml.pole(G)/(2*math.pi), ml.zero(G)/(2*math.pi))

    mag, phase, w = ml.bode(G, Hz=True)
    print(mag, phase, w)
    # mag, phase, w = ml.bode(G)

    plt.show()


if __name__ == '__main__':
    # num = np.array([2.37, 16580150, 100000000])
    # den = np.array([2.37, 1580150, 100000000])
    # drawtf(num, den)

    # num2 = np.array([2.37, 1580000+1.5*10**7])
    # den2 = np.array([2.37, 1580000])
    # drawtf(num2, den2)

    # num3 = np.array([0.1658, 1])
    # den3 = np.array([0.0158, 1])
    # drawtf(num3, den3)

    # num4 = np.array([0.8295, 16580])
    # den4 = np.array([0.8295, 1580])
    # drawtf(num4, den4)

    num5 = np.array([0.9948, 1])
    den5 = np.array([0.0948, 1])
    drawtf(num5, den5)
