from gpiozero import Button

class RelaisMonitor:
    def __init__(self, pin, callback):
        self.relais = Button(pin, pull_up=True, bounce_time=0.1)  # 100ms debounce
        self.relais.when_pressed = lambda: callback(True)
        self.relais.when_released = lambda: callback(False)