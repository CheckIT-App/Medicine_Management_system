try:
    import pigpio
except ImportError:
    # Mock pigpio for non-Raspberry Pi environments
    class MockPigpio:
        OUTPUT = 1  # Mimic pigpio.OUTPUT
        INPUT = 0   # Mimic pigpio.INPUT

        def __init__(self):
            print("Mock pigpio initialized (running on non-Raspberry Pi).")

        def pi(self):
            return self

        def connected(self):
            return False

        def set_mode(self, pin, mode):
            print(f"Mock: Set mode for pin {pin} to {mode}.")

        def write(self, pin, value):
            print(f"Mock: Write value {value} to pin {pin}.")

        def stop(self):
            print("Mock: Stopping pigpio.")
    
    pigpio = MockPigpio()

import asyncio
from math import sqrt
import time

class MotorControl:
    def __init__(self, config):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Error: pigpio daemon is not running.")

        # Extract pin configurations
        self.X_DIR_PIN = config["X_DIR_PIN"]
        self.X_PUL_PIN = config["X_PUL_PIN"]
        self.X_ENA_PIN = config["X_ENA_PIN"]

        self.Y_DIR_PIN = config["Y_DIR_PIN"]
        self.Y_PUL_PIN = config["Y_PUL_PIN"]
        self.Y_ENA_PIN = config["Y_ENA_PIN"]

        self.STEP_DELAY_MAX = config.get("STEP_DELAY_MAX", 0.05)  # Default value if not provided
        self.STEP_DELAY_MIN = config.get("STEP_DELAY_MIN", 0.005)  # Default value if not provided
        self.STEPS_PER_MM = config.get("STEPS_PER_MM", 100)  # Default value if not provided
        self.ACCELERATION_STEPS = config.get("ACCELERATION_STEPS", 50)  # Default value if not provided
        self.toggle_ena_pin = config.get("TOGGLE_ENA_PIN", True)  # Default: toggle ENA_PIN

        # Configure GPIO pins for X motor
        self.pi.set_mode(self.X_ENA_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.X_DIR_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.X_PUL_PIN, pigpio.OUTPUT)

        # Configure GPIO pins for Y motor
        self.pi.set_mode(self.Y_ENA_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.Y_DIR_PIN, pigpio.OUTPUT)
        self.pi.set_mode(self.Y_PUL_PIN, pigpio.OUTPUT)

        if self.toggle_ena_pin:
            # disable both motors
            self.pi.write(self.X_ENA_PIN, 1)  # disable X motor driver
            self.pi.write(self.Y_ENA_PIN, 1)  # disable Y motor driver
        else:
            self.pi.write(self.X_ENA_PIN, 0)  # Enable X motor driver
            self.pi.write(self.Y_ENA_PIN, 0)  # Enable Y motor driver

    async def move_motor(self, dir_pin, pul_pin, ena_pin, steps):
        """Move a motor asynchronously with adjusted acceleration and deceleration."""
        direction = 1 if steps > 0 else 0
        steps = abs(steps)

        if self.toggle_ena_pin:
            # Enable motor
            print("Enabling motor driver")
            self.pi.write(ena_pin, 0)  # Enable motor driver

        self.pi.write(dir_pin, direction)

        # Determine effective acceleration steps based on total steps
        effective_acceleration_steps = min(self.ACCELERATION_STEPS, steps // 2)

        # Calculate the max speed reached during acceleration
        max_speed_delay = self.STEP_DELAY_MAX - (
            (effective_acceleration_steps / self.ACCELERATION_STEPS) * (self.STEP_DELAY_MAX - self.STEP_DELAY_MIN)
        )

        # Accelerate
        for i in range(effective_acceleration_steps):
            delay = self.STEP_DELAY_MAX - (i / self.ACCELERATION_STEPS) * (self.STEP_DELAY_MAX - self.STEP_DELAY_MIN)
            self.pi.write(pul_pin, 1)
            await asyncio.sleep(delay)
            self.pi.write(pul_pin, 0)
            await asyncio.sleep(delay)

        # Constant speed phase (if steps allow)
        constant_speed_steps = steps - 2 * effective_acceleration_steps
        for _ in range(constant_speed_steps):
            self.pi.write(pul_pin, 1)
            await asyncio.sleep(max_speed_delay)
            self.pi.write(pul_pin, 0)
            await asyncio.sleep(max_speed_delay)

        # Decelerate
        for i in range(effective_acceleration_steps):
            delay = max_speed_delay + (i / self.ACCELERATION_STEPS) * (self.STEP_DELAY_MAX - max_speed_delay)
            self.pi.write(pul_pin, 1)
            await asyncio.sleep(delay)
            self.pi.write(pul_pin, 0)
            await asyncio.sleep(delay)

        if self.toggle_ena_pin:
            # Disable motor
            self.pi.write(ena_pin, 1)  # Disable motor driver


    async def move_to_position(self, target_x, target_y):
        steps_x = int(target_x * self.STEPS_PER_MM)
        steps_y = int(target_y * self.STEPS_PER_MM)

        await asyncio.gather(
            self.move_motor(self.X_DIR_PIN, self.X_PUL_PIN, self.X_ENA_PIN, steps_x),
            self.move_motor(self.Y_DIR_PIN, self.Y_PUL_PIN, self.Y_ENA_PIN, steps_y)
        )

    def calculate_distance(self, current, target):
        """Calculate the Euclidean distance between two points."""
        return sqrt((current[0] - target[0]) ** 2 + (current[1] - target[1]) ** 2)

    async def collect_medicine(self, amount):
        print(f"collected {amount}" )
        
    async def optimized_dispense_medicines(self, medicines):
        """
        Dispense a list of medicines with optimized movement.
        Each medicine has a target X, Y, and an amount to dispense.
        """
        if not medicines:
            print("No medicines to dispense.")
            return

        # Sort medicines by distance from the starting position (0, 0)
        current_position = (0, 0)
        sorted_medicines = []

        while medicines:
            # Find the nearest medicine
            nearest = min(
                medicines,
                key=lambda med: self.calculate_distance(current_position, (med["x"], med["y"])),
            )
            sorted_medicines.append(nearest)
            current_position = (nearest["x"], nearest["y"])
            medicines.remove(nearest)

        # Dispense sorted medicines
        for medicine in sorted_medicines:
            x, y, amount = medicine["x"], medicine["y"], medicine["amount"]
            print(f"Moving to position X: {x}, Y: {y} to dispense {amount} units.")
            await self.move_to_position(x, y)
            await self.collect_medicine(amount)
            print(f"Finished dispensing {amount} units at position X: {x}, Y: {y}.")
    
    def cleanup(self):
        """Cleanup GPIO and stop pigpio."""
        self.pi.write(self.X_ENA_PIN, 1)  # Disable X motor driver
        self.pi.write(self.Y_ENA_PIN, 1)  # Disable Y motor driver
        self.pi.stop()
