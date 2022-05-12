from itertools import groupby
from typing.calendar import (
    CalendarEvent,
    CalendarEventCategory,
    CalendarEventName,
    CalendarName,
)
from typing.generic import Contact, DateTime, Location
from typing.message import Content
from typing.navigation import TrafficCondition
from typing.reminders import Content
from typing.weather import WeatherCondition, WeatherTemperature
from queries.apps import AppsQuery
from queries.navigation import NavigationQuery
from queries.weather import WeatherQuery
from queries.messages import MessagesQuery
from queries.calendar import CalendarQuery
from queries.reminders import RemindersQuery
from commands.messages import MessagesCommand
from commands.reminders import RemindersCommand
from commands.responder import ResponderCommand
from data_utils import first, last, day_of_the_week


"""
Example: ”Get the weather in London and Brussels today and tomorrow”
"""
location = Location.resolve_from_text("London and Brussels")
date_time = DateTime.resolve_from_text("today and tomorrow")
weather_forecasts = WeatherQuery.get_weather_forecasts(
    location=location, date_time=date_time
)

ResponderCommand.default_responder(response=weather_forecasts)


"""
Example: "Tell me every stand up show tonight in the city at 8 pm"
"""

event_category = CalendarEventCategory.resolve_from_text("stand up show")
date_time = DateTime.resolve_from_text("tonight")
location = Location.resolve_from_text("in the city")
date_time2 = DateTime.resolve_from_text("at 8 pm")

calendar_events = CalendarQuery.get_calendar_events(
    location=location, date_time=date_time, category=event_category
)
calendar_events = filter(
    CalendarEvent.get_predicate(date_time=date_time2), calendar_events
)

ResponderCommand.default_responder(response=calendar_events)


"""
Example: "Create a reminder for the Monday appointment while cancelling all other reminders for today"
"""
date_time = DateTime.resolve_from_text("Monday")
calendar_events = CalendarQuery.get_calendar_events(date_time=date_time)
calendar_events = first(calendar_events)
reminder = RemindersCommand.create_reminder(calendar_event=calendar_events)

date_time = DateTime.resolve_from_text("today")
reminders = RemindersQuery.get_reminders(date_time=date_time)
for x in reminders:
    if x != reminder:
        RemindersCommand.delete_reminders(reminders=x)


"""
Example: "Text mom and dad about the Saturday brunch and the matinee"
"""
contact1 = Contact.resolve_from_text("mom")
contact2 = Contact.resolve_from_text("dad")

brunch = CalendarEventName.resolve_from_text("Saturday brunch")
saturday = DateTime.resolve_from_text("Saturday")
calendar_events = CalendarQuery.get_calendar_events(
    date_time=saturday, event_name=brunch
)
event1 = first(calendar_events)

matinee = CalendarEventName.resolve_from_text("the matinee")
calendar_events = CalendarQuery.get_calendar_events(event_name=matinee)
event2 = first(calendar_events)

for contact in [contact1, contact2]:
    for event in [event1, event2]:
        MessagesCommand.send_message(recipient=contact, exact_content=event)


"""
Example: "Text your mom and my dad about the Saturday brunch and the matinee"
"""
contact1 = Contact.resolve_from_text("your mom")
contact2 = Contact.resolve_from_text("my dad")
event_name = CalendarEventName.resolve_from_text("Saturday brunch")
date_time = DateTime.resolve_from_text("Saturday")
calendar_events = CalendarQuery.get_calendar_events(
    date_time=date_time, event_name=event_name
)
event1 = first(calendar_events)

event_name = CalendarEventName.resolve_from_text("the matinee")
calendar_events = CalendarQuery.get_calendar_events(event_name=matinee)
event2 = first(calendar_events)

for contact in [contact1, contact2]:
    for event in [event1, event2]:
        MessagesCommand.send_message(recipient=contact, exact_content=event)


"""
Read me the first and last meeting for each day of the week I have on my calendar
"""
date_time = DateTime.resolve_from_text("the week")
calendar = CalendarName.resolve_from_text("my calendar")
calendar_events = CalendarQuery.get_calendar_events(
    date_time=date_time, calendar=calendar
)
calendar_events = sorted(calendar_events)

days = map(lambda x: day_of_the_week(x.date_time), calendar_events)
days = list(set(days))
for day in days:
    daily_calendar_events = filter(
        lambda x: day_of_the_week(x.date_time), calendar_events
    )
    first_item = first(daily_calendar_events)
    ResponderCommand.default_responder(response=first_item)
    last_item = last(daily_calendar_events)
    if last_item and last_item != first_item:
        ResponderCommand.default_responder(response=last_item)

# weekly_meetings = groupby(meetings, lambda x: day_of_the_week(x.date_time))
# for day, daily_meetings in weekly_meetings:
#     first_meeting = first(daily_meetings)
#     last_meeting = last(daily_meetings) if len(list(daily_meetings)) > 1 else None
#     ResponderCommand.default_responder(response=first_meeting)
#     if last_meeting:
#         ResponderCommand.default_responder(response=last_meeting)
