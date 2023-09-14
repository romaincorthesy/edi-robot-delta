class IInputDevice:
    def __init__(self, screen_width = 1440, screen_height = 900):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.callbackUpdate = None

    def updatePosition(self, x:int, y:int):
        raise NotImplementedError


class Mouse(IInputDevice):
    def updatePosition(self, x: int, y: int):
        self.x = x
        self.y = y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)


class Touchfoil(IInputDevice):
    import ScreenConversion as SC

    def updatePosition(self, x: int, y: int):
        touch_x = int(self.SC.remap(self.screen_height, 0, 0, self.screen_width, y))
        touch_y = int(self.SC.remap(0, self.screen_width, 0, self.screen_height, x))

        self.x = touch_x
        self.y = touch_y

        if self.callbackUpdate is not None:
            self.callbackUpdate(self)
