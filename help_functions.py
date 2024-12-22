from constants import *
from datetime import timedelta


def get_interval(
        current_time: timedelta,
        total_buses: int,
        road_time: float
) -> timedelta:
    """
    Рассчитывает интервал выпуска автобусов для равномерного покрытия маршрута.

    Args:
        current_time (timedelta): Текущее время.
        total_buses (int): Общее количество автобусов.
        road_time (int): Время полного маршрута в минутах (включая остановки и развороты).

    Returns:
        timedelta: Интервал выпуска автобусов.
    """
    current_hour: int = int(current_time.total_seconds() // SECONDS_IN_HOUR) % HOUR_IN_DAY

    if total_buses > 0:
        base_interval: float = road_time / total_buses
    else:
        return timedelta(minutes=road_time)

    current_day: int = current_time.days % DAYS_IN_WEEK
    if WEEKDAYS_START <= current_day <= WEEKDAYS_END:
        if (PEAK_HOURS_MORNING_START <= current_hour < PEAK_HOURS_MORNING_END) or \
                (PEAK_HOURS_EVENING_START <= current_hour < PEAK_HOURS_EVENING_END):
            adjusted_interval: float = base_interval * PEAK_MULTIPLIER
        elif REGULAR_HOURS_START <= current_hour < REGULAR_HOURS_END:
            adjusted_interval = base_interval * REGULAR_MULTIPLIER
        else:
            adjusted_interval = base_interval * NIGHT_MULTIPLIER
        return timedelta(minutes=adjusted_interval)

    else:
        if WEEKEND_REGULAR_START_HOUR <= current_hour < WEEKEND_REGULAR_END_HOUR:
            adjusted_interval: float = base_interval * REGULAR_MULTIPLIER
        else:
            adjusted_interval = base_interval * NIGHT_MULTIPLIER

        return timedelta(minutes=adjusted_interval)


def is_weekday(current_day: int) -> bool:
    """
    Проверяет, является ли текущий день рабочим днём (понедельник - пятница).

    Args:
        current_day (int): Текущий день недели (0 - понедельник, 6 - воскресенье).

    Returns:
        bool: True, если рабочий день, иначе False.
    """
    return current_day < 5  # Понедельник - пятница


def can_8h_work(current_hour: int, current_day: int) -> bool:
    """
    Проверяет, можно ли выпустить 8-часового водителя в текущий момент.

    Args:
        current_hour (int): Текущий час (0-23).
        current_day (int): Текущий день недели (0 - понедельник, 6 - воскресенье).

    Returns:
        bool: True, если можно выпустить 8-часового водителя, иначе False.
    """
    return is_weekday(current_day) and 5 <= current_hour < 22
