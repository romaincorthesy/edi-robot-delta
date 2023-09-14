# Source github user: laundmo (https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56)
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.

    Examples
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)

    """
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.

    Examples
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)

    """
    return (v - a) / (b - a)


def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.

    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.

    Examples
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)

    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))
