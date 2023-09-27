#!/usr/bin/env python3

from math import *
import random
from functools import cache

# Number of decimals
GM_PRECISION = 3

# Robot dimensions in [m]
L_a: float = 0.091
L_b: float = 0.166
R: float = 0.100


# Constants
theta: tuple[None, float, float, float] = (None, 0.0, 2*pi/3, 4*pi/3)
nb_axes: int = 3
op_dim: int = 3


@cache
def Rot_Inv_Geometric_Model(X_in: tuple[float, float, float]) -> tuple[tuple[float, float, float], int]:
    X = [None, X_in[0], X_in[1], X_in[2]]

    # print(X)

    error_id: int = 0

    S: float = (1/L_a)*(-X[1]**2 - X[2]**2 - X[3]**2 + L_b**2 - L_a**2 - R**2)

    T: tuple[None, float, float, float] = [None, 0, 0, 0]
    Q: tuple[None, float, float, float] = [None, 0, 0, 0]

    for i in range(1, 4):
        T[i] = 2*X[1]*cos(theta[i]) + 2*X[2]*sin(theta[i])
        Q[i] = 2*atan((-2*X[3] - sqrt(4*X[3]**2 + 4*R**2 - S**2 + T[i]**2 * (1 -
                      R**2/L_a**2) + T[i]*(-2*R*S/L_a - 4*R))) / (-2*R - S - T[i]*(R/L_a - 1)))
        if (-2*R - S - T[i]*(R/L_a - 1)) == 0:
            error_id = -1

    # -pi/4 because the coordonates system has 90° offset in motor position
    return ([q-pi/2 for q in Q[1:]], error_id)


@cache
def Rot_Dir_Geometric_Model(Q_in: tuple[float, float, float]) -> tuple[tuple[float, float, float], int]:
    Q = [i+pi/2 for i in [None, Q_in[0], Q_in[1], Q_in[2]]]

    error_id: int = 0

    D = [None, 0, 0, 0]
    E = [None, 0, 0, 0]
    F = [None, 0, 0, 0]
    G = [None, 0, 0, 0]
    gamma = [None, 0, 0, 0]
    beta = [None, 0, 0, 0]

    for i in range(1, 4):
        D[i] = -L_b**2 + L_a**2 + R**2 + 2*R*L_a*cos(Q[i])
        E[i] = 2*(R + L_a*cos(Q[i]))*cos(theta[i])
        F[i] = 2*(R + L_a*cos(Q[i]))*sin(theta[i])
        G[i] = -2*L_a*sin(Q[i])

    H_1 = E[1]*G[2] - E[1]*G[3] - E[2]*G[1] + E[2]*G[3] + E[3]*G[1] - E[3]*G[2]
    H_2 = -E[1]*F[2] + E[1]*F[3] + E[2] * \
        F[1] - E[2]*F[3] - E[3]*F[1] + E[3]*F[2]
    H_3 = -E[1]*D[2] + E[1]*D[3] + E[2] * \
        D[1] - E[2]*D[3] - E[3]*D[1] + E[3]*D[2]
    H_4 = F[1]*D[2] - F[1]*D[3] - F[2]*D[1] + F[2]*D[3] + F[3]*D[1] - F[3]*D[2]
    H_5 = -F[1]*G[2] + F[1]*G[3] + F[2] * \
        G[1] - F[2]*G[3] - F[3]*G[1] + F[3]*G[2]

    if H_2 == 0:
        error_id = -1
        X = [None, 0, 0, 0]
        return (X[1:], error_id)

    L = (H_5**2 + H_1**2)/H_2**2 + 1
    M = 2*(H_5*H_4 + H_1*H_3)/H_2**2 - (H_5*E[1] + H_1*F[1])/H_2 - G[1]
    N = (H_4**2 + H_3**2)/H_2**2 - (H_4*E[1] + H_3*F[1])/H_2 + D[1]

    if L == 0:
        error_id = -2
        X = [None, 0, 0, 0]
        return (X[1:], error_id)
    else:
        rac = M**2 - 4*L*N
        if rac < 0:
            error_id = -3
            X = [None, 0, 0, 0]
            return (X[1:], error_id)
        else:
            z = (-M - sqrt(rac))/(2*L)

    x = z*(H_5/H_2) + H_4/H_2
    y = z*(H_1/H_2) + H_3/H_2

    X = [None, x, y, z]

    for i in range(1, 4):
        C_i = [
            None,
            (R + L_a*cos(Q[i]))*cos(theta[i]),
            (R + L_a*cos(Q[i]))*sin(theta[i]),
            -L_a*sin(Q[i])
        ]
        # only P_i[3] is used so can be optimized
        P_i = [None, X[1] - C_i[1], X[2] - C_i[2], X[3] - C_i[3]]
        d = abs(sin(theta[i])*X[1] - cos(theta[i])*X[2] -
                sin(theta[i])*C_i[1] + cos(theta[i])*C_i[2])
        gamma[i] = asin(d/L_b)
        beta[i] = asin(abs(P_i[3])/(L_b*cos(gamma[i])))

    gammaMax = 40/180*pi

    if gamma[1] < -gammaMax or gamma[1] > gammaMax:
        error_id = -4

    if gamma[2] < -gammaMax or gamma[2] > gammaMax:
        error_id = -5

    if gamma[3] < -gammaMax or gamma[3] > gammaMax:
        error_id = -6

    if Q[1] + beta[1] < 30/180*pi or Q[1] + beta[1] > pi:
        error_id = -7

    if Q[2] + beta[2] < 30/180*pi or Q[2] + beta[2] > pi:
        error_id = -8

    if Q[3] + beta[3] < 30/180*pi or Q[3] + beta[3] > pi:
        error_id = -9

    # print(f"Direct gonna return ({X[1:]},{error_id})")
    return (X[1:], error_id)


# Timing tests
# Last check :
#   36.75925313899825 seconds
#   GM error: 71714, Math domain error: 35104, BaseException:0, total err: 106818, Tries: 1000000 -> 10.681799999999999% error

def IGM(X_op: tuple[float, float, float]) -> tuple[float, float, float]:
    Q_art: tuple[float, float, float] = None
    X_op_rounded = tuple([round(x, GM_PRECISION) for x in X_op])

    Q_art, err = Rot_Inv_Geometric_Model(X_op_rounded)
    if err != 0:
        raise ArithmeticError(
            f"Rot_Inv_Geometric_Model returned error number {err}")
    Q_art = [round(q, GM_PRECISION) for q in Q_art]

    return Q_art


def DGM(Q_art: tuple[float, float, float]) -> tuple[float, float, float]:
    X_op: tuple[float, float, float] = None
    Q_art_rounded = tuple(
        [round(q, GM_PRECISION) for q in Q_art])

    X_op, err = Rot_Dir_Geometric_Model(Q_art_rounded)
    if err != 0:
        raise ArithmeticError(
            f"Rot_Dir_Geometric_Model returned error number {err}")
    X_op = [round(x, GM_PRECISION) for x in X_op]

    return X_op


err = aerr = verr = tot = 0
GM_PRECISION = 3


def test():
    global err, aerr, verr, tot
    x = random.randrange(-100, 100, 5)/1000.0
    y = random.randrange(-100, 100, 5)/1000.0
    z = random.randrange(-150, -100, 5)/1000.0
    try:
        angles = IGM((x, y, z))
        pos = DGM(angles)
    except ArithmeticError:
        aerr += 1
    except ValueError:
        verr += 1
    except BaseException:
        err += 1
    finally:
        tot += 1


if __name__ == '__main__':
    import timeit
    import random
    print(str(timeit.timeit("test()", setup="from __main__ import test")) + " seconds")
    print(
        f"GM error: {aerr}, Math domain error: {verr}, BaseException:{err}, total err: {aerr+verr+err}, Tries: {tot} -> {((aerr+verr+err)/tot)*100}% error")
