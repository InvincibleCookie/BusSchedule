from constants import *
from datetime import timedelta
from models import BusDriver
from drivers_movement import drivers_movement
from get_and_check_drivers import check_drivers
from typing import List
from initialization import initialize
import pandas as pd


def simulate_time(
        simulation_duration: int,
        n_of_stations: int,
        n_of_buses: int,
        n_of_drivers_eight_shift: int,
        n_of_drivers_twelve_shift: int,
) -> pd.DataFrame:
    """
    Симулирует работу системы автобусов за заданный период времени.

    Эта функция инициализирует станции, автобусы и водителей, затем запускает цикл симуляции,
    обновляя состояния водителей и автобусов каждую минуту.

    Args:
        simulation_duration (int): Продолжительность симуляции в минутах.
        n_of_stations (int): Общее количество остановок.
        n_of_buses (int): Количество автобусов в прямом направлении.
        n_of_drivers_eight_shift (int): Количество водителей с 8-часовыми сменами.
        n_of_drivers_twelve_shift (int): Количество водителей с 12-часовыми сменами.

    Returns:
        pd.DataFrame: DataFrame с состояниями водителей на протяжении симуляции.
    """
    # Инициализация станций, автобусов и водителей
    stations, buses, drivers = initialize(
        n_of_stations,
        n_of_buses,
        n_of_drivers_eight_shift,
        n_of_drivers_twelve_shift
    )

    active_drivers: List['BusDriver'] = []
    finished_drivers: List['BusDriver'] = []
    drivers_on_lunch: List['BusDriver'] = []
    df: pd.DataFrame = pd.DataFrame(columns=[PLACEHOLDER_COLUMN], dtype=object)
    df.index.name = "Time_index"
    current_time: timedelta = timedelta(hours=SIMULATION_START_HOURS)
    simulation_end: timedelta = timedelta(minutes=simulation_duration) + current_time

    last_dispatch_time_direct: timedelta = INITIAL_DISPATCH_TIME
    last_dispatch_time_reverse: timedelta = INITIAL_DISPATCH_TIME

    while current_time < simulation_end:

        # Обновление состояний водителей и автобусов
        df = drivers_movement(
            active_drivers=active_drivers,
            finished_drivers=finished_drivers,
            drivers_on_lunch=drivers_on_lunch,
            buses=buses,
            df=df,
            current_time=current_time
        )

        if finished_drivers:
            for driver in finished_drivers:
                driver.between_shifts_time -= TIME_INCREMENT
                driver.update_day_off()

        # Диспетчеризация новых водителей
        last_dispatch_time_direct, last_dispatch_time_reverse = check_drivers(
            current_time=current_time,
            finished_drivers=finished_drivers,
            active_drivers=active_drivers,
            drivers=drivers,
            buses=buses,
            last_dispatch_time_direct=last_dispatch_time_direct,
            last_dispatch_time_reverse=last_dispatch_time_reverse
        )

        # Увеличиваем текущее время на одну минуту
        current_time += TIME_INCREMENT

    print("Симуляция завершена.")
    print("Всего водителей:", len(active_drivers) + len(finished_drivers))
    return df
