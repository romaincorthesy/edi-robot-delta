class IInputDevice:
    """Interface describing an input device capable of providing a position on the screen.

    Attributes:
        screen_width (int): the width of the display in px. Defaults to 1440.
        screen_height (int): the height of the display in px. Defaults to 900.
        callbackUpdate (func) : the function to call when the position is updated. Defaults to None.
    """

    def __init__(self, screen_width: int = 1440, screen_height: int = 900, screen_usable_width: int = 900, screen_usable_height: int = 900) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_usable_width = screen_usable_width
        self.screen_usable_height = screen_usable_height

        self.callbackUpdate = None

    def updatePosition(self, x: int, y: int) -> None:
        """Empty placeholder to be overidden by subclasses. Update the position attributes.

        Args:
            x (int): x position on the screen
            y (int): y position on the screen

        Raises:
            NotImplementedError: because it's meant to be overidden.
        """
        raise NotImplementedError


class Mouse(IInputDevice):
    """Class describing a mouse capable of providing a position on the screen.

    Attributes:
        screen_width (int): the width of the display in px. Defaults to 1440.
        screen_height (int): the height of the display in px. Defaults to 900.
        callbackUpdate (func) : the function to call when the position is updated. Defaults to None.
    """

    def updatePosition(self, x: int, y: int) -> None:
        """Update the position attributes and then call the update callback if it exists.

        Args:
            x (int): x position on the screen
            y (int): y position on the screen
        """
        self.x = x
        self.y = y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)


class Touchfoil(IInputDevice):
    """Class describing a touch foil capable of providing a position on the screen.

    Attributes:
        screen_width (int): the width of the display in px. Defaults to 1440.
        screen_height (int): the height of the display in px. Defaults to 900.
        callbackUpdate (func) : the function to call when the position is updated. Defaults to None.
    """
    import ScaleConversion as SC

    def updatePosition(self, x: int, y: int) -> None:
        """Update the position attributes with converted values and then call the update callback if it exists.

        Args:
            x (int): x position on the screen
            y (int): y position on the screen
        """
        touch_x = int(self.SC.remap(
            self.screen_height, 0, 0, self.screen_width, y))
        touch_y = int(self.SC.remap(
            0, self.screen_width, 0, self.screen_height, x))

        self.x = touch_x
        self.y = touch_y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)
