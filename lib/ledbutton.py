from machine import Pin
from neopixel import NeoPixel


class CNAMES:
    RED = (200, 0, 0)
    GREEN = (0, 200, 0)
    BLUE = (0, 0, 200)
    YELLOW = (200, 100, 0)
    PURPLE = (150, 0, 150)
    ORANGE = (225, 30, 0)
    WHITE = (100, 100, 100)
    SKY = (0, 200, 100)
    PINK = (225, 0, 30)


class SingleLed:
    OFF = (0, 0, 0)

    def __init__(self, pin_num, rgb=CNAMES.WHITE, cname=None, n_leds=1):
        self._leds_count = n_leds
        self.np = NeoPixel(
            Pin(pin_num, Pin.OUT),
            n_leds
        )
        self.set_color(rgb=rgb, cname=cname)

    def set_color(self, rgb=None, cname=None):
        if cname is not None:
            rgb = getattr(CNAMES, cname.upper())
        if rgb is None:
            raise ValueError(f"One of 'rgb' or 'cname' have to be not None!")
        self.color = rgb

    def on(self, rgb=None, cname=None):
        if cname is not None or rgb is not None:
            self.set_color(rgb=rgb, cname=cname)
        for led_pos in range(self._leds_count):
            self.np[led_pos] = self.color
        self.np.write()

    def off(self):
        for led_pos in range(self._leds_count):
            self.np[led_pos] = self.OFF
        self.np.write()


class Button:
    def __init__(self, pin_num, color=None):
        self._pin_num = pin_num
        self.p = Pin(
            pin_num,
            mode=Pin.IN,
            pull=Pin.PULL_DOWN
        )
        self.p.off()
        self.color = color

    def is_pressed(self):
        return self.p.value() == 1

    def is_released(self):
        return self.p.value() == 0

    def __str__(self):
        return f"Button(pin_num={self._pin_num}, color={self.color}, pressed={self.is_pressed})"


class ButtonPad:
    def __init__(self):
        self._buttons = dict()
        self._colors = dict()
        self._cname = None

    def add_button(self, pin, color):
        self._buttons[color] = Button(pin, color)
        self._colors[color] = getattr(CNAMES, color.upper())

    def check_pressed(self):
        for color, button in self._buttons.items():
            if button.is_pressed():
                self._cname = color
                return

    @property
    def color(self):
        if self._cname is not None:
            return self._colors[self._cname]

    def __getattr__(self, cname):
        try:
            return self._buttons[cname]
        except KeyError:
            raise KeyError(f"ButtonPad have no button {cname}. {self}")

    def __str__(self):
        return f"ButtonPad(buttons={self._buttons}, _cname={self._cname})"
