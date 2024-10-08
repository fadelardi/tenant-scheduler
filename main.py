from datetime import datetime
from src.entities import Runner, Zone, Tenant, Apartment, Visit
from src.appointment_check import is_slot_available


def exec():
    date = datetime(2024, 1, 1, 9)
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone)
    visit = Visit(apartment, tenant, date)

    if is_slot_available(visit, [], []):
        print(f"Scheduled: APT {apartment.id} at {date}")
    else:
        print(f"Failed: APT {apartment.id} at {date}")

if __name__ == "__main__":
    exec()
