from constants import *
from datetime import timedelta
from models import Bus, BusDriver
from help_functions import get_interval
from typing import List
import pandas as pd


def drivers_movement(
        active_drivers: List['BusDriver'],
        finished_drivers: List['BusDriver'],
        drivers_on_lunch: List['BusDriver'],
        buses: List['Bus'],
        df: pd.DataFrame,
        current_time: timedelta
) -> pd.DataFrame:
    """
    Обрабатывает действия водителей автобусов, включая движение, перерывы и завершение смены.

    Эта функция обновляет состояние водителей и автобусов, записывая информацию в DataFrame.

    Args:
        active_drivers (List[BusDriver]): Список активных водителей.
        finished_drivers (List[BusDriver]): Список завершивших работу водителей.
        drivers_on_lunch (List[BusDriver]): Список водителей на перерыве.
        buses (List[Bus]): Список автобусов
        df (pd.DataFrame): DataFrame для отслеживания состояния водителей.
        current_time (timedelta): Текущее время.

    Returns:
        pd.DataFrame: Обновленный DataFrame со статусами водителей.
    """
    time_str = f"{current_time.days % DAYS_IN_WEEK}, {current_time - timedelta(hours=current_time.days * HOUR_IN_DAY)}"

    if time_str not in df.index:
        df.loc[time_str] = [pd.NA] * len(df.columns)

    dispatch_interval = get_interval(current_time, N_OF_BUS, FLOAT_ROAD_TIME)

    for driver in active_drivers[:]:
        if driver.name not in df.columns:
            df[driver.name] = pd.NA
            df.at[time_str, driver.name] = [
                "Вышел на смену",
                f"Смена: {driver.shift_duration}",
                f"Автобус: {driver.bus.number if driver.bus else 'Не назначен'}"
            ]

        if not driver.is_allowed_to_work(DEFAULT_TO_NEXT * N_OF_STATIONS, current_time):
            df.at[time_str, driver.name] = [
                f"Закончил смену",
                f"Смена: {driver.shift_duration}",
                f"Автобус: {driver.bus.number}"
            ]
            driver.end_of_the_day(active_drivers, finished_drivers, buses)
            continue

        if driver.on_lunch:
            if driver.end_break(drivers_on_lunch, buses, active_drivers, finished_drivers):
                df.at[time_str, driver.name] = [
                    "Закончил перерыв",
                    f"Смена: {driver.shift_duration}",
                    f"Автобус: {driver.bus.number}"
                ]
            continue
        else:
            if driver.shift_duration == SHIFT_DURATION_8H:
                if driver.working_time >= WORKING_TIME_THRESHOLD_8H and driver.daily_breaks > 0 and driver.bus.station == START_STATION:
                    df.at[time_str, driver.name] = [
                        "Ушел на перерыв",
                        f"Смена: {driver.shift_duration}",
                        "Автобус: None"
                    ]
                    driver.take_break(buses, drivers_on_lunch)
                    continue
            else:
                if (
                        (driver.working_time >= WORKING_TIME_THRESHOLD_12H_FIRST and
                         driver.daily_breaks == 2 and
                         driver.bus.station == START_STATION) or
                        (driver.working_time >= WORKING_TIME_THRESHOLD_12H_SECOND and
                         driver.daily_breaks == 1 and
                         driver.bus.station == START_STATION)
                ):
                    df.at[time_str, driver.name] = [
                        "Ушел на перерыв",
                        f"Смена: {driver.shift_duration}",
                        "Автобус: None"
                    ]
                    driver.take_break(buses, drivers_on_lunch)
                    continue

        driver.working_time += TIME_INCREMENT

        reached_station = driver.drive_bus()

        if reached_station:
            station = driver.bus.station
            if station not in (0, N_OF_STATIONS):
                df.at[time_str, driver.name] = [
                    f"На остановке {(station) if driver.bus.direct else (N_OF_STATIONS + station)}",
                    f"Смена: {driver.shift_duration}",
                    f"Автобус: {driver.bus.number}"
                ]
            else:
                df.at[time_str, driver.name] = [
                    f"В депо",
                    f"Смена: {driver.shift_duration}",
                    f"Автобус: {driver.bus.number}"
                ]

    return df
