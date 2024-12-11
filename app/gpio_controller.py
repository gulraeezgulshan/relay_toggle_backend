import RPi.GPIO as GPIO

class RelayController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.relay_pins = {
            1: 17,  # GPIO17
            2: 27,  # GPIO27
            3: 22,  # GPIO22
            4: 23,  # GPIO23
        }

        for pin in self.relay_pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH) 
    
    def control_relay(self, relay_port: int, status: str):
        """Control relay based on device status"""
        if relay_port not in self.relay_pins:
            raise ValueError(f"Invalid relay port: {relay_port}")
            
        pin = self.relay_pins[relay_port]
        if status in ['on', 'open']:
            GPIO.output(pin, GPIO.LOW) 
        else:
            GPIO.output(pin, GPIO.HIGH)

    def cleanup(self):
        """Cleanup GPIO on program exit"""
        GPIO.cleanup()