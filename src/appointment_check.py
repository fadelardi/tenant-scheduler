from datetime import datetime, timedelta
from src.entities import Apartment, Holiday, Visit
from src.constants import VISITING_DAYS, MIN_VISITING_HR, MAX_VISITING_HR

def apt_avail(slot_date: datetime, apt: Apartment) -> bool:
    avail = True
    if apt.avail_days is not None:
        if slot_date.weekday() not in apt.avail_days:
            avail = False

    if avail and apt.avail_times is not None:
        avail = False
        for start, end in apt.avail_times:
            if start <= slot_date <= end:
                avail = True
                break

    return avail

def runner_avail(date: datetime, runner_id:int, holidays: list[Holiday]|None = None) -> bool:
    if holidays is None:
        return True

    available = True

    for holiday in holidays:
        if holiday.runner.id == runner_id:
            if holiday.start <= date <= holiday.end:
                available = False
                break

    return available

def visited_yesterday(new_visit_date: datetime, scheduled_visit_date: datetime) -> bool:
    yesterday_delta = timedelta(days=1) 
    if new_visit_date.weekday() == 0:
        yesterday_delta = timedelta(days=3) 

    yesterday = new_visit_date - yesterday_delta 
    return scheduled_visit_date == yesterday
    

def over_visit_limit(new_visit: Visit, scheduled_visits:list[Visit]) -> bool:
    """limit criteria: > 30 weekly visit, consecutive days, slot visitors > 2, runner returning to zone"""
    new_visit_date = new_visit.date
    new_visit_apartment = new_visit.apartment
    cur_weekday = new_visit_date.weekday()
    week_start = new_visit_date - timedelta(days=cur_weekday)
    week_end = new_visit_date + timedelta(days=5-cur_weekday)
    week_visits = 1
    slot_visits = {}
    runner_id = new_visit.apartment.runner.id
    prior_visit_list = []
    date_day_fmt = "%y%m%d"

    for scheduled_visit in scheduled_visits:

        scheduled_date = scheduled_visit.date
        is_visit_today = scheduled_date.strftime(date_day_fmt) == new_visit_date.strftime(date_day_fmt) 
        scheduled_apartment = scheduled_visit.apartment

        # is it the same apartment?
        if scheduled_apartment.id == new_visit_apartment.id:
            # is it the same slot?
            if scheduled_date == new_visit_date:
                cur_visits = slot_visits.get(new_visit_apartment.id, 0)
                slot_visits.update({ new_visit_apartment.id: cur_visits + 1 })
                
                # does it have over two visitors?
                if slot_visits[new_visit_apartment.id] == 2:
                    return True
                
            # is the scheduled visit within the week of the new visit?
            if week_start <= scheduled_date <= week_end: 
                week_visits += 1

            # are there 30 or more visits, or was this apartment already seen yesterday?
            if week_visits > 30 or visited_yesterday(new_visit_date, scheduled_date):
                return True

        # different apartment, same slot
        elif scheduled_date == new_visit_date:
            return False

            
        # is this visit the same runner and is it before this appointment today?
        if scheduled_apartment.runner.id == runner_id and is_visit_today and scheduled_date < new_visit_date:
            prior_visit_list.append(scheduled_visit)

    # if there are prior visits this day, and last visit is in another zone
    if len(prior_visit_list) > 0 and prior_visit_list[-1].apartment.zone != new_visit_apartment.zone:

        # iterate through all zones prior to last zone
        for prior_visit in prior_visit_list[:-1]:

            # has the zone been already visited? 
            if prior_visit.apartment.zone == new_visit_apartment.zone:
                return True

    return False

def valid_date(new_visit_date: datetime) -> bool:
    """check to see if date is MON-FRI 9-17 and that it is a valid 15 min slot"""
    weekday = new_visit_date.weekday()
    hour = new_visit_date.hour
    minute = new_visit_date.minute
    second = new_visit_date.second
    valid_day = weekday in VISITING_DAYS
    valid_hour = MIN_VISITING_HR <= hour <= MAX_VISITING_HR
    valid_time = valid_hour and minute in [0,15,30,45] and second == 0

    return valid_day and valid_time 


def is_slot_available(new_visit: Visit, scheduled_visits: list[Visit], holidays: list[Holiday]|None = None) -> bool:
    """determine if the desired slot for the new visit is available"""
    visit_date = new_visit.date
    apartment = new_visit.apartment
    apartment_runner = apartment.runner.id

    available = False
    if valid_date(visit_date): 
        if apt_avail(visit_date, apartment):
            if runner_avail(visit_date, apartment_runner, holidays):
                if not over_visit_limit(new_visit, scheduled_visits): 
                    available = True

    return available

