from datetime import datetime, timedelta
from src.entities import Apartment, Holiday, Runner, Tenant, Visit, Zone
from src.appointment_check import is_slot_available

def test_apartment_day_not_avail():
    date = datetime(2024, 1, 1, 9)
    another_date = datetime(2024, 1, 2)
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone, avail_days=[another_date.weekday()])
    apartment2 = Apartment(id=1, runner=runner, zone=zone, avail_days=[date.weekday()])
    visit = Visit(apartment, tenant, date)
    visit2 = Visit(apartment2, tenant, date)

    assert is_slot_available(visit2, [])
    assert not is_slot_available(visit, [])

def test_apartment_time_not_avail():
    date = datetime(2024, 1, 1, 10)
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone, avail_times=[(date - timedelta(minutes=30), date + timedelta(minutes=30))])
    apartment2 = Apartment(id=1, runner=runner, zone=zone, avail_times=[(date - timedelta(hours=1), date - timedelta(minutes=30))])
    visit = Visit(apartment, tenant, date)
    visit2 = Visit(apartment2, tenant, date)

    assert is_slot_available(visit, [])
    assert not is_slot_available(visit2, [])

def test_runner_on_holidays():
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone)
    date = datetime(2024, 1, 1, 9)

    holidays = [
        Holiday(runner, start=date - timedelta(days=1), end=date + timedelta(days=2))
    ]

    visit = Visit(apartment, tenant, date)

    assert is_slot_available(visit, [])
    assert not is_slot_available(visit, [], holidays)

def test_consecutive_day_limit():
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone)
    date = datetime(2024, 1, 1, 9)

    visit = Visit(apartment, tenant, date)
    visit2 = Visit(apartment, tenant, date + timedelta(days=1))

    assert not is_slot_available(visit2, [visit])

def test_weekly_limit():
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone)
    date = datetime(2024, 1, 1, 9)

    visit = Visit(apartment, tenant, date)
    scheduled_visits = [visit] * 30

    assert not is_slot_available(visit, scheduled_visits)

def test_daily_zone_limit():
    runner = Runner(id=0)
    zone = Zone(id=0)
    zone2 = Zone(id=2)
    tenant = Tenant(id=0)
    apartment = Apartment(id=0, runner=runner, zone=zone)
    apartment2 = Apartment(id=1, runner=runner, zone=zone2)
    date = datetime(2024, 1, 1, 13)

    visit = Visit(apartment, tenant, date)
    scheduled_visits = [
        Visit(apartment, tenant, date - timedelta(hours=1, minutes=15)),
        Visit(apartment2, tenant, date - timedelta(hours=1))
    ]

    assert not is_slot_available(visit, scheduled_visits)

def test_time_slot_full():
    runner = Runner(id=0)
    zone = Zone(id=0)
    tenants = [Tenant(id=0), Tenant(id=1), Tenant(id=2)]
    apartment = Apartment(id=0, runner=runner, zone=zone)
    date = datetime(2024, 1, 1, 9)

    visit = Visit(apartment, tenants[2], date)
    scheduled_visits = [
        Visit(apartment, tenants[0], date),
        Visit(apartment, tenants[1], date)
    ]

    assert is_slot_available(visit, [])
    assert not is_slot_available(visit, scheduled_visits)

