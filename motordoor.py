from gpiozero import Servo
from time import sleep

class ServoMotor:
    def __init__(self, gpio_pin, correction=0):
        """
        Initialize the ServoMotor class.
        :param gpio_pin: GPIO pin number (BCM mode)
        :param correction: Correction value to adjust the minimum and maximum pulse width
        """
        self.gpio_pin = gpio_pin
        self.correction = correction
        self.min_pulse_width = (1.0 - self.correction) / 1000  # Minimum pulse width
        self.max_pulse_width = (2.0 + self.correction) / 1000  # Maximum pulse width
        
        # Create a Servo object but do not attach initially
        self.servo = Servo(self.gpio_pin, 
                           min_pulse_width=self.min_pulse_width, 
                           max_pulse_width=self.max_pulse_width)
        self.servo.detach()  # Ensure no PWM signal is sent initially

    def set_angle(self, angle):
        """
        Set the servo motor angle.
        :param angle: Angle value, range 0-180
        """
        if not (0 <= angle <= 180):
            raise ValueError("Angle must be between 0 and 180")
        
        # Attach the servo to start sending PWM signals
        self.servo.value = None  # Reattach the servo
        # Convert the angle to Servo.value range (-1.0 to 1.0)
        servo_value = (angle / 180.0) * 2 - 1.0
        self.servo.value = servo_value
        print(f"Set angle: {angle}-> Servo value: {servo_value:.2f}")
        sleep(0.5)  # Allow the servo to move
        self.servo.detach()  # Stop sending PWM signals
        print("PWM signal stopped after operation.")

    def cleanup(self):
        """
        Clean up resources.
        """
        self.servo.detach()
        print("Servo motor has been released")

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the servo motor object
        servo_motor = ServoMotor(gpio_pin=13)
        servo_motor.set_angle(90)
        while True:
            # Input command
            command = input("Enter command ('open', 'close', 'exit' to quit): ")
            if command.lower() == "exit":
                break
            
            if command.lower() == "open":
                servo_motor.set_angle(180)
            elif command.lower() == "close":
                servo_motor.set_angle(90)
            else:
                print("Invalid command. Please enter 'open', 'close', or 'exit'.")

    except KeyboardInterrupt:
        print("Program interrupted!")

    finally:
        servo_motor.cleanup()
        print("Program terminated.")
