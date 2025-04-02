from machine import Pin, Timer
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
    def __init__(
            self,
            pin_num,
            color=None,
            use_internal_resistor=True,
            debounce_timer=None,
            debounce_timer_id=3,
            debounce_period_ms=10
        ):
        if debounce_timer is not None:
            self._debounce_timer = debounce_timer
        else:
            self._debounce_timer = Timer(debounce_timer_id)
        self._debounce_period_ms = debounce_period_ms
        self._pin_num = pin_num
        self.p = Pin(
            pin_num,
            mode=Pin.IN,
            pull=Pin.PULL_DOWN if use_internal_resistor else None
        )
        self.p.off()
        self.color = color
        self.was_pressed = 0
        if not use_internal_resistor:
            self.p.irq(
                handler=self.start_debounce_timer,
                trigger=Pin.IRQ_RISING
            )

    def start_debounce_timer(self, pin):
        self._debounce_timer.init(
            mode=Timer.ONE_SHOT,
            period=self._debounce_period_ms,
            callback=self.set_was_pressed
        )

    def set_was_pressed(self, timer):
        self.was_pressed = 1

    def is_pressed(self):
        return self.p.value() == 1

    def __str__(self):
        return f"Button(pin_num={self._pin_num}, color={self.color}, pressed={self.is_pressed})"


class ButtonPad:
    def __init__(
            self,
            use_internal_resistor=False,
            debounce_timer=None,
            debounce_timer_id=3,
            debounce_period_ms=10
        ):
        if debounce_timer is not None:
            self._debounce_timer = debounce_timer
        else:
            self._debounce_timer = Timer(debounce_timer_id)
        self._debounce_period_ms = debounce_period_ms
        self._use_internal_resistor = use_internal_resistor
        self._buttons = dict()
        self._colors = dict()
        self._cname = None

    def add_button(self, pin, color):
        self._buttons[color] = Button(
            pin_num=pin,
            color=color,
            debounce_timer=self._debounce_timer,
            use_internal_resistor=self._use_internal_resistor,
            debounce_period_ms=self._debounce_period_ms
        )
        self._colors[color] = getattr(CNAMES, color.upper())

    def check_pressed(self):
        for color, button in self._buttons.items():
            if button.was_pressed == 1:
                button.was_pressed = 0
                self._cname = color
                return
            
    def reset(self):
        self._cname = None
        for button in self._buttons.values():
            button.was_pressed = 0

    @property
    def rgb_color(self):
        if self._cname is not None:
            return self._colors[self._cname]
        
    @property
    def color_name(self):
        return self._cname

    def __getattr__(self, cname):
        try:
            return self._buttons[cname]
        except KeyError:
            raise KeyError(f"ButtonPad have no button {cname}. {self}")

    def __str__(self):
        return f"ButtonPad(buttons={self._buttons}, _cname={self._cname})"
