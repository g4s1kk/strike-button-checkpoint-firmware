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


class Led:
  OFF = (0, 0, 0)

  def __init__(self, pin_num, cname=CNAMES.WHITE):
    self.np = NeoPixel(
      Pin(pin_num, Pin.OUT),
      1
    )
    self.set_color(cname)

  def set_color(self, cname):
    self.color = cname

  def on(self, cname=None):
    if cname is not None:
      self.set_color(cname)
    self.np[0] = self.color
    self.np.write()

  def off(self):
    self.np[0] = self.OFF
    self.np.write()


class Button:
  def __init__(self, pin_num):
    self.p = Pin(pin_num, Pin.IN)
    self.p.off()

  def is_pressed(self):
    return self.p.value() == 1

  def is_released(self):
    return self.p.value() == 0

