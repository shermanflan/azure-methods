import logging

from client.api.crm import (
    get_patients, get_patient
)
from client.api.ci import (
    get_instances, get_entity
)
import client.util.log_config

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # CRM
    get_patient(by_filter="pah_name eq 'Saitama Sensei'")

    # CI
    get_instances()

    entities = [
        "Customer",
        "Dynamics365_PatientPhysician",
        "Dynamics365_PatientCensus",
        "Dynamics365_PatientAllergy",
        "Dynamics365_PatientAppointment",
        "Dynamics365_PatientMedication",
        "Dynamics365_Patient",
        "FrameworkLTC_FrameworkPatient",
        "FrameworkLTC_FrameworkRxOrder",
        "FrameworkLTC_RxOrderCompare",
    ]

    get_entity(name="Customer")

    logger.info(f"Processing complete...")
