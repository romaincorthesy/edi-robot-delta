#!/usr/bin/env python3


# To find Inverse Kinematics Of A Delta Robot
# Reference:
# Paper Name: The Delta Parallel Robot: Kinematics Solutions; Author name: Robert L. Williams II, Ph.D, Mechanical Engineering, Ohio University; Date: October 2016
# Please download the above mentioned paper. It has been kept in https://github.com/giridharanponnuvel/Delta-Robot-Inverse-Kinematics. Thank You!
########################################################################################################################
# Author: Giridharan P
# Date: 16-03-2019
# Credits: Thanks to Asst.Prof Rajeev Lochana G C, Mechanical Department, Amrita School of Engineering, Bangalore
########################################################################################################################
########################################################################################################################
# Note:
# Refer Page 4 & 5, Before you go through this code. Delta robot kinemtatics diagram is given over there.
########################################################################################################################
import math
import cmath

Sb = 0.433013  # Base equilateral triangle side (Incircle radius : 0.125m)
# Platform equilateral triangle side (Circumcircle radius : 0.125m)
Sp = 0.043301
L = 0.091   # Upper legs length
l = 0.166   # Lower legs parallelogram length
########################################################################################################################


def getAnglesDegreesFromPosition(position: tuple[float, float, float], min_theta: float, max_theta: float, silent: bool = False) -> tuple[float, float, float]:
    x, y, z = position

    # We don't use Solution 2 because the angles are reversed and offset by
    rep1, rep2 = IGM(x, y, z, silent)

    # Correct for different coordinate system
    sol2 = [-(rep-90) for rep in rep2]

    if not silent:
        print("Solution 2 in real angles:")
        for index, sol in enumerate(sol2):
            print(f'\u03F42{index}: {sol}')
        print()

    sol2_ok = True
    for angle in sol2:
        if angle > max_theta:
            if sol2_ok == True:
                print(f"sol2 refused because {angle} > {max_theta}")
            sol2_ok = False
        elif angle < min_theta:
            if sol2_ok == True:
                print(f"sol2 refused because {angle} < {min_theta}")
            sol2_ok = False

    if not silent:
        print(f"sol2_ok: {sol2_ok}")

    if sol2_ok:
        return sol2
    else:
        # raise ArithmeticError("No solution found")
        if not silent:
            print(f"No solution found for {x},{y},{z}")
        return ()


def IGM(x: float, y: float, z: float, silent: bool = False):
    ########################################################################################################################
    # Wb,Ub,Wp,Up declaration:
    # Refer Page: 6
    Wb = float(((math.sqrt(3)) / 6) * Sb)
    Ub = float(((math.sqrt(3)) / 3) * Sb)
    Wp = float(((math.sqrt(3)) / 6) * Sp)
    Up = float(((math.sqrt(3)) / 3) * Sp)
    if not silent:
        print("Wb:", Wb)
        print("Ub:", Ub)
        print("Wp:", Wp)
        print("Up:", Up)
    ########################################################################################################################
    # Refer Page: 11
    a = float(Wb - Up)
    b = float((Sp * 0.5) - (((math.sqrt(3)) * 0.5) * Wb))
    c = float(Wp - (0.5 * Wb))
    if not silent:
        print("a:", a)
        print("b:", b)
        print("c:", c)
        print()
    ########################################################################################################################
    # Inverse Kinematics:
    # Refer Page: 12
    E1 = float(2 * L * (y + a))

    F1 = float(2 * z * L)

    G1 = float(
        math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2) + math.pow(a, 2) + math.pow(L, 2) + (2 * y * a) - (math.pow(l, 2)))

    E2 = float(-L * (((math.sqrt(3)) * (x + b)) + y + c))

    F2 = float(2 * z * L)

    G2 = float(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2) + math.pow(b, 2) + math.pow(c, 2) + math.pow(L, 2) + (
        2 * ((x * b) + (y * c))) - math.pow(l, 2))

    E3 = float(L * (((math.sqrt(3)) * (x - b)) - y - c))

    F3 = float(2 * z * L)

    G3 = float(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2) + math.pow(b, 2) + math.pow(c, 2) + math.pow(L, 2) + (
        2 * (-(x * b) + (y * c))) - math.pow(l, 2))

    if not silent:
        print("E1:", E1)
        print("F1:", F1)
        print("G1:", G1)
        print("E2:", E2)
        print("F2:", F2)
        print("G2:", G2)
        print("E3:", E3)
        print("F3:", F3)
        print("G3:", G3)
        print()
    ########################################################################################################################
    # EFG : Pre-Processing  the variables:
    # Refer Page: 12
    # Quadratic Formula throws few error if we compile all togather hence few operations are pre-processed
    E1Sqr = math.pow(E1, 2)
    F1Sqr = math.pow(F1, 2)
    G1Sqr = math.pow(G1, 2)

    E2Sqr = math.pow(E2, 2)
    F2Sqr = math.pow(F2, 2)
    G2Sqr = math.pow(G2, 2)

    E3Sqr = math.pow(E3, 2)
    F3Sqr = math.pow(F3, 2)
    G3Sqr = math.pow(G3, 2)
    ########################################################################################################################
    EFGsum1 = (E1Sqr + F1Sqr - G1Sqr)
    EFGsum2 = (E2Sqr + F2Sqr - G2Sqr)
    EFGsum3 = (E3Sqr + F3Sqr - G3Sqr)
    ########################################################################################################################
    if EFGsum1 < 0:
        EFG_1 = -(cmath.sqrt(EFGsum1)).imag
    else:
        EFG_1 = math.sqrt(EFGsum1)

    if EFGsum2 < 0:
        EFG_2 = -(cmath.sqrt(EFGsum2)).imag
    else:
        EFG_2 = math.sqrt(EFGsum2)

    if EFGsum3 < 0:
        EFG_3 = -(cmath.sqrt(EFGsum3)).imag
    else:
        EFG_3 = math.sqrt(EFGsum3)

    if not silent:
        print("########################################################################################################################")
        print()
    # Inverse Kinematics Solution 1:
    if not silent:
        print("Solution 1:")
    T11 = float((-(F1) + EFG_1) / (G1 - E1))
    theta11 = 2 * (math.degrees(math.atan(T11)))
    if not silent:
        print('\u03F4''11:', theta11)

    T12 = float((-(F2) + EFG_2) / (G2 - E2))
    theta12 = 2 * (math.degrees(math.atan(T12)))
    if not silent:
        print('\u03F4''12:', theta12)

    T13 = float((-(F3) + EFG_3) / (G3 - E3))
    theta13 = 2 * (math.degrees(math.atan(T13)))
    if not silent:
        print('\u03F4''13:', theta13)

    ########################################################################################################################
    # Inverse Kinematics Solution 2:
    if not silent:
        print("Solution 2:")
    T21 = float((-(F1) - EFG_1) / (G1 - E1))
    theta21 = 2 * (math.degrees(math.atan(T21)))
    if not silent:
        print('\u03F4''21:', theta21)

    T22 = float((-(F2) - EFG_2) / (G2 - E2))
    theta22 = 2 * (math.degrees(math.atan(T22)))
    if not silent:
        print('\u03F4''22:', theta22)

    T23 = float((-(F3) - EFG_3) / (G3 - E3))
    theta23 = 2 * (math.degrees(math.atan(T23)))
    if not silent:
        print('\u03F4''23:', theta23)

    if not silent:
        print()

    return ((theta11, theta12, theta13), (theta21, theta22, theta23))


# TESTS
MAX_ITERATIONS = 50
iterations = 0


def findPositionForAngle(min_z: float, max_z: float, goal: float, decimal_pos: int) -> float:
    global iterations
    iterations += 1
    if iterations > MAX_ITERATIONS:
        return None

    mid_z = (max_z+min_z)/2
    _, _, angle = getAnglesDegreesFromPosition(
        (0, 0, mid_z), -21, 46, silent=True)

    print(
        f"Testing {min_z} - {mid_z} - {max_z} and getting {angle}° for mid", end="")

    if round(angle, decimal_pos) == goal:
        print("\n")
        return mid_z
    elif angle < goal:
        print(" (mid_z too small)")
        return findPositionForAngle(mid_z, max_z, goal, decimal_pos)
    elif angle > goal:
        print(" (mid_z too big)")
        return findPositionForAngle(min_z, mid_z, goal, decimal_pos)


def listAnglesForZ():
    list_z = []
    for z in range(-278, 0, 1):
        rep1, rep2 = IGM(0, 0, z/1000.0, True)
        # Correct for different coordinate system
        sol1 = [-(rep-90) for rep in rep1]
        sol2 = [-(rep-90) for rep in rep2]
        list_z.append((z/1000.0, (sol1[0], sol2[0])))

    return list_z


if __name__ == "__main__":
    list_z = listAnglesForZ()

    with open("./output_angles_list_GM2.csv", 'w') as f:
        print("Pos_z [m],Solution1 [°],Solution2[°]", file=f)
        for z, (sol1, sol2) in list_z:
            print(f"{z},{sol1},{sol2}", file=f)

    decimal_pos = 2

    # # 0°
    # min_z = -0.256
    # max_z = -0.255
    # goal = 0

    # 14.11
    min_z = -0.250
    max_z = -0.240
    goal = 14.11

    print(
        f"Looking for position where angles are at {goal}° ({decimal_pos} decimals precision)\n")
    res = findPositionForAngle(min_z, max_z, goal, decimal_pos)
    if res is not None:
        print(f"Found position for angle {goal}° : (0,0,{res}) [m]")
    else:
        print(f"Couldn't find a position in {MAX_ITERATIONS} iterations")
