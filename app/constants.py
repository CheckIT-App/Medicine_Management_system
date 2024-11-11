from enum import Enum
from gettext import gettext as _  # Assuming gettext is correctly configured

class Steps(Enum):
    SCAN_BARCODE = 1
    ENTER_MEDICINE_DETAILS = 2
    PLACE_IN_STORAGE = 3
    RESCAN_FOR_AUTHORIZATION = 4
    CONFIRMATION = 5

    @property
    def label(self):
        labels = {
            Steps.SCAN_BARCODE: _("Scan Barcode"),
            Steps.ENTER_MEDICINE_DETAILS: _("Medicine Details"),
            Steps.PLACE_IN_STORAGE: _("Place in Storage"),
            Steps.RESCAN_FOR_AUTHORIZATION: _("Re-scan for Authorization"),
            Steps.CONFIRMATION: _("Confirmation"),
        }
        return labels[self]

    @property
    def loading_message(self):
        loading_message = {
            Steps.SCAN_BARCODE: _("Processing barcode"),
            Steps.ENTER_MEDICINE_DETAILS: _("Opening storage"),
            Steps.PLACE_IN_STORAGE: "",  # Empty string remains unchanged
            Steps.RESCAN_FOR_AUTHORIZATION: _("Processing barcode"),
            Steps.CONFIRMATION: "",
        }
        return loading_message[self]
    
class DispenseSteps(Enum):
    SCAN_PATIENT_BARCODE = 1
    SELECT_MEDICINES = 2
    DISPENSING_AND_COMPLETE = 3  # Combined step for dispensing and completion

    @property
    def label(self):
        labels = {
            DispenseSteps.SCAN_PATIENT_BARCODE: _("Scan Patient Barcode"),
            DispenseSteps.SELECT_MEDICINES: _("Select Medicines"),
            DispenseSteps.DISPENSING_AND_COMPLETE: _("Dispensing Medicines"),
        }
        return labels[self]
    
    @property
    def loading_message(self):
        loading_message = {
            DispenseSteps.SCAN_PATIENT_BARCODE: _("Processing barcode"),
            DispenseSteps.SELECT_MEDICINES: _("Dispensing medicines. Please wait..."),
            DispenseSteps.DISPENSING_AND_COMPLETE: "",
        }
        return loading_message[self]
