# Source github user: laundmo (https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56)
from functools import cache

@cache
def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.

    Args:
        a (float): min scale value
        b (float): max scale value
        t (float): value to interpolate on the scale

    Returns:
        float: the interpolated value
    
    Examples:
        50 == lerp(0, 100, 0.5)\n
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b

@cache
def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.

    Args:
        a (float): min scale value
        b (float): max scale value
        v (float): value of interrest on the scale

    Returns:
        float: fraction (between 0 and 1) of the scale where v is

    Examples:
        0.5 == inv_lerp(0, 100, 50)\n
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)

@cache
def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.

    Args:
        i_min (float): min value of the scale on which the original value resides
        i_max (float): max value of the scale on which the original value resides
        o_min (float): min value of the scale to which it should be mapped
        o_max (float): max value of the scale to which it should be mapped
        v (float): value to remap

    Returns:
        float: remaped value

    Examples
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))
