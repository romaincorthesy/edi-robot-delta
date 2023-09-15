class IInputDevice:
    def __init__(self, screen_width: int = 1440, screen_height: int = 900) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.callbackUpdate = None

    def updatePosition(self, x:int, y:int) -> None:
        raise NotImplementedError


class Mouse(IInputDevice):
    def updatePosition(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)


class Touchfoil(IInputDevice):
    import ScreenConversion as SC

    def updatePosition(self, x: int, y: int) -> None:
        touch_x = int(self.SC.remap(self.screen_height, 0, 0, self.screen_width, y))
        touch_y = int(self.SC.remap(0, self.screen_width, 0, self.screen_height, x))

        self.x = touch_x
        self.y = touch_y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)
