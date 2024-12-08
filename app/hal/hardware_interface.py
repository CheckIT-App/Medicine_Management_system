# hardware_interface.py
import time
import asyncio

class HardwareInterface:
    def __init__(self):
        # Initialization for hardware components like the barcode scanner and storage lock
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
        # Simulate dispensing time based on the number of medicines
        dispensing_time = len(selected_medicines) * 1  # Example: 1 second per medicine
        print("Dispensing medicines:", selected_medicines)
        
        # Simulate awaiting hardware response
        await asyncio.sleep(dispensing_time)  # Wait for the simulated dispensing time

        print("Medicines dispensed.")
        return True
