from constants import *
from datetime import timedelta
from models import Bus, BusDriver
from help_functions import get_interval
from typing import List, Optional, Tuple
import math


def get_driver(
        finished_drivers: List['BusDriver'],
        drivers: List['BusDriver'],
        current_hour: int,
        current_day: int
) -> Optional['BusDriver']:
    """
    Находит подходящего водителя из завершивших смену или из пула доступных водителей.

    Args:
        direction (bool): Направление движения (True - прямое, False - обратное).
        finished_drivers (List[BusDriver]): Список водителей, завершивших смену.
        drivers (List[BusDriver]): Пул водителей, готовых к работе.
        current_hour (int): Текущий час (0-23).
        current_day (int): Текущий день недели (0 - понедельник, 6 - воскресенье).

    Returns:
        Tuple[Optional[BusDriver], List[BusDriver]]: Найденный водитель или None, обновлённый список завершивших водителей.
    """
    allow_8_hour: bool = (5 <= current_hour < 22 and current_day in range(0, 5))
    for driver in finished_drivers[:]:
        if allow_8_hour and driver.shift_duration == SHIFT_DURATION_8H:
            if driver.between_shifts_time <= timedelta(minutes=0):
                driver.between_shifts_time = timedelta(hours=11)
                finished_drivers.remove(driver)
                return driver
        elif not allow_8_hour and driver.shift_duration == SHIFT_DURATION_12H:
            if driver.can_work_today and driver.between_shifts_time <= timedelta(minutes=0):
                driver.between_shifts_time = timedelta(hours=11)
                finished_drivers.remove(driver)
                return driver
    for drv in drivers:
        if allow_8_hour and drv.shift_duration == SHIFT_DURATION_8H:
            drivers.remove(drv)
            return drv
        elif not allow_8_hour and drv.shift_duration == SHIFT_DURATION_12H:
            drivers.remove(drv)
            return drv
    return None


def check_drivers(
        current_time: timedelta,
        finished_drivers: List['BusDriver'],
        active_drivers: List['BusDriver'],
        drivers: List['BusDriver'],
        buses: List['Bus'],
        last_dispatch_time_direct: timedelta,
        last_dispatch_time_reverse: timedelta
) -> Tuple[timedelta, timedelta]:
    """
    Проверяет и распределяет новых водителей на автобусы в зависимости от текущего времени и состояния водителей.

    Эта функция рассчитывает необходимое количество автобусов для текущего времени,
    находит подходящих водителей из завершивших смену или доступных пулов водителей,
    назначает им автобусы и обновляет время последней диспетчеризации.

    Args:
        current_time (timedelta): Текущее время симуляции.
        finished_drivers (List[BusDriver]): Список водителей, завершивших смену.
        active_drivers (List[BusDriver]): Список активных водителей.
        drivers (List[BusDriver]): Пул водителей.
        buses (List[Bus]): Список автобусов, движущихся в прямом направлении.
        last_dispatch_time_direct (timedelta): Время последней диспетчеризации для прямого направления.
        last_dispatch_time_reverse (timedelta): Время последней диспетчеризации для обратного направления.

    Returns:
        Tuple[timedelta, timedelta]: Обновлённые времена последней диспетчеризации для прямого и обратного направлений.
    """
    total_minutes: float = current_time.total_seconds() // MINUTES_PER_HOUR
    current_hour: int = int(total_minutes // MINUTES_PER_HOUR) % HOUR_IN_DAY
    dispatch_interval: timedelta = get_interval(current_time, N_OF_BUS, FLOAT_ROAD_TIME)

    interval_minutes: float = dispatch_interval.total_seconds() // MINUTES_PER_HOUR
    required_buses: int = math.ceil(FLOAT_ROAD_TIME / interval_minutes)

    current_day: int = current_time.days % 7

    needed_buses: int = required_buses - len(active_drivers) // 2

    for _ in range(needed_buses):
        if last_dispatch_time_direct + dispatch_interval <= current_time or last_dispatch_time_direct == timedelta(
                hours=0):
            last_dispatch_time_direct = current_time
            driver = get_driver(finished_drivers, drivers, current_hour, current_day)
            if driver:
                if driver.bus_for_driver(buses):
                    driver.bus.direct = True
                    active_drivers.append(driver)

        if last_dispatch_time_reverse + dispatch_interval <= current_time or last_dispatch_time_reverse == timedelta(
                hours=0):
            last_dispatch_time_reverse = current_time
            driver_rev = get_driver(finished_drivers, drivers, current_hour, current_day)
            if driver_rev:
                if driver_rev.bus_for_driver(buses):
                    driver_rev.bus.direct = False
                    active_drivers.append(driver_rev)

    return last_dispatch_time_direct, last_dispatch_time_reverse
