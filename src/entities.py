from dataclasses import dataclass
from datetime import datetime, time

@dataclass
class Tenant:
    id:int

@dataclass
class Runner:
    id:int

@dataclass 
class Holiday:
    runner:Runner
    start:datetime
    end:datetime

@dataclass
class Zone:
    id:int
    
@dataclass
class Apartment:
    id:int
    runner:Runner
    zone:Zone
    avail_days:list[int]|None = None
    avail_times:list[tuple[datetime, datetime]]|None = None

@dataclass
class Visit:
    apartment:Apartment
    tenant:Tenant
    date:datetime
