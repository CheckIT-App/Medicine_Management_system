# hardware_interface.py
import time
import asyncio

from app.hal.motor_control import MotorControl

class HardwareInterface:
    def __init__(self, config):
        # Initialization for hardware components like the barcode scanner and storage lock
        self.config = config
        self.motor_control = None  # Placeholder for motor control
        self.scanner_initialized = False
        self.storage_lock_initialized = False
        self.initialized = False

        # Call initialization
        self.initialize_all_hardware()

    def initialize_all_hardware(self):
        """
        Initialize all hardware components.
        """
        self.motor_control = MotorControl(self.config)
        self.scanner_initialized = self.initialize_scanner()
        self.storage_lock_initialized = self.initialize_storage_lock()
        self.initialized = self.initialize_hardware()

    def initialize_scanner(self):
        # Initialize scanner hardware (mocked for demonstration)
        print("Barcode scanner initialized.")
        return True

    def initialize_storage_lock(self):
        # Initialize storage lock hardware (mocked for demonstration)
        print("Storage lock initialized.")
        return True

    def initialize_hardware(self):
        # Setup for hardware initialization
        print("Hardware initialized.")
        return True

    async def scan_barcode(self):
        # Trigger the barcode scanner and get the scanned data
        # Simulated delay to account for hardware response time
        await asyncio.sleep(1)  # Simulated hardware delay
        scanned_data = "1"  # Mocked barcode data
        print(f"Scanned barcode: {scanned_data}")
        return scanned_data

    async def open_storage(self):
        # Send a command to open the storage (mocked)
        print("Opening storage...")
        await asyncio.sleep(2)  # Simulate hardware delay
        print("Storage is open.")
        return True

    async def close_storage(self):
        # Send a command to close the storage (mocked)
        print("Closing storage...")
        await asyncio.sleep(2)  # Simulate hardware delay
        print("Storage is closed.")
        return True

    async def put_medicine(self, target_x, target_y):
        """Function to move medicine to a specific position."""
        
        try:
            # Move to target position
            await self.motor_control.move_to_position(target_x, target_y)
            print(f"Medicine moved to position X: {target_x}, Y: {target_y}.")
        finally:
            # Cleanup resources
            self.motor_control.cleanup()
        # def get_patient_medicines(self, patient_barcode):
        #     # Simulated database lookup for patient’s active medicines
        #     patient_medicines = {
        #         "111111111": [
        #             {"id": "med1", "name": "Aspirin", "dosage": "100mg"},
        #             {"id": "med2", "name": "Paracetamol", "dosage": "500mg"}
        #         ]
        #     }
        #     return patient_medicines.get(patient_barcode, [])

    async def dispense_medicines(self, selected_medicines):
        """
        Dispense a list of medicines by calling optimized_dispense_medicines.
        Each selected medicine is validated and prepared for optimized dispensing.
        """
        try:
            if not selected_medicines:
                print("No medicines selected for dispensing.")
                return

            # Prepare the medicine data for optimized dispensing
            medicines = []
            for med in selected_medicines:
                if "x" not in med or "y" not in med or "amount" not in med:
                    print(f"Skipping invalid medicine entry: {med}")
                    continue

                medicines.append({
                    "x": med["x"],
                    "y": med["y"],
                    "amount": med["amount"]
                })

            if not medicines:
                print("No valid medicines to dispense.")
                return

            # Call optimized dispensing
            await self.motor_control.optimized_dispense_medicines(medicines)

        except Exception as e:
            print(f"An error occurred during dispensing: {e}")

