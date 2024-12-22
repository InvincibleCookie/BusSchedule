from constants import *
from datetime import timedelta
from typing import List, Optional


class Bus:
    """
    Класс Bus представляет автобус с определенным номером, текущей станцией, направлением движения и состоянием.

    Attributes:
        number (int): Номер автобуса.
        direct (bool): Флаг, который показывает, в какую сторону едет автобус.
        to_next (int): Время до следующей остановки.
    """

    def __init__(self, number: int, direct: bool) -> None:
        """
        Инициализирует объект Bus.

        Args:
            number (int): Номер автобуса.
            direct (bool): Флаг, который показывает, в какую сторону едет автобус.
        """
        self.number: int = number
        self.station: int = START_STATION
        self.direct: bool = direct
        self.to_next: int = DEFAULT_TO_NEXT

    def move(self) -> bool:
        """
        Функция, которая отвечает за движение автобуса к следующей станции.

        Проходит минута и мы ближе к следующей остановке.

        Если to_next = 0, то мы доехали до следующей станции.
        В таком случае, если мы не в депо, то обновляем нашу станцию.
        Если в депо - Обновляем положение, возвращаясь на стартовое положение

        Returns:
            bool: True, если автобус достиг остановки, иначе False.
        """
        self.to_next -= timedelta(minutes=1)

        if self.to_next == timedelta(minutes=0):
            if self.direct:
                self.station += 1
            else:
                self.station -= 1

            self.to_next = DEFAULT_TO_NEXT
            if abs(self.station) == N_OF_STATIONS:
                self.station = START_STATION
                self.to_next = DEFAULT_TO_NEXT
            return True
        return False


class BusDriver:
    """
    Класс BusDriver представляет водителя автобуса с определенными характеристиками и поведением.

    Attributes:
        name (str): Имя водителя.
        shift_duration (timedelta): Продолжительность смены.
        bus (Optional[Bus]): Привязанный автобус.
        on_lunch (bool): Флаг, указывающий на перерыв.
        working_time (timedelta): Время работы за день.
        days_worked (int): Дни, отработанные подряд.
        all_rest (timedelta): Общее время отдыха за день.
        resting_time (timedelta): Время, которое водитель на отдыхе.
        between_shifts_time (timedelta): Время между сменами.
        daily_breaks (int): Количество перерывов за смену.
        break_duration (timedelta): Продолжительность перерыва.
        can_work_today (bool): Флаг, указывающий, может ли водитель работать сегодня.
        day_off (timedelta): Время, оставшееся до следующего рабочего дня.
    """

    def __init__(
            self,
            name: str,
            shift_duration: timedelta,
            bus: Optional['Bus'],
    ) -> None:
        """
        Инициализирует объект BusDriver.

        Args:
            name (str): Имя водителя.
            shift_duration (timedelta): Продолжительность смены.
            bus (Optional[Bus]): Привязанный автобус.
        """
        self.name: str = name
        self.shift_duration: timedelta = shift_duration
        self.bus: Optional['Bus'] = bus
        self.on_lunch: bool = False
        self.working_time: timedelta = timedelta(hours=0)
        self.days_worked: int = 0
        self.all_rest: timedelta = timedelta(hours=0)
        self.resting_time: timedelta = timedelta(minutes=0)
        self.between_shifts_time: timedelta = BETWEEN_SHIFTS_TIME

        if self.shift_duration == DEFAULT_SHIFT_DURATION_12H:
            self.daily_breaks: int = DAILY_BREAKS_12H
            self.break_duration: timedelta = BREAK_DURATION_12H
            self.can_work_today: bool = True
            self.day_off: timedelta = timedelta(hours=0)
        else:
            self.daily_breaks: int = DAILY_BREAKS_8H
            self.break_duration: timedelta = BREAK_DURATION_8H

    def bus_for_driver(self, bus_pool: List['Bus']) -> bool:
        """
        Назначает автобус водителю из пула свободных автобусов.

        Args:
            bus_pool (List[Bus]): Пул доступных автобусов.

        Returns:
            bool: True, если автобус был назначен, иначе False.
        """
        if bus_pool:
            self.bus = bus_pool.pop(0)
            return True
        return False

    def release_bus_from_driver(self, bus_pool: List['Bus']) -> None:
        """
        Освобождает автобус от водителя и возвращает его в пул.

        Args:
            bus_pool (List[Bus]): Пул доступных автобусов.
        """
        if self.bus:
            self.bus.direct = None
            bus_pool.append(self.bus)
            self.bus = None

    def take_break(self, bus_pool: List['Bus'], drivers_on_lunch: List['BusDriver']) -> None:
        """
        Отправляет водителя на перерыв.

        Args:
            bus_pool (List[Bus]): Пул доступных автобусов.
            drivers_on_lunch (List[BusDriver]): Список водителей на перерыве.
        """
        self.release_bus_from_driver(bus_pool)
        self.daily_breaks -= 1
        self.on_lunch = True
        drivers_on_lunch.append(self)

    def end_break(
            self,
            drivers_on_lunch: List['BusDriver'],
            bus_pool: List['Bus'],
            active_drivers: List['BusDriver'],
            finished_drivers: List['BusDriver']
    ) -> bool:
        """
        Завершает перерыв водителя и возвращает его к работе, если перерыв закончен.

        Args:
            drivers_on_lunch (List[BusDriver]): Список водителей на перерыве.
            bus_pool (List[Bus]): Пул доступных автобусов.
            active_drivers (List[BusDriver]): Список активных водителей.
            finished_drivers (List[BusDriver]): Список завершивших работу водителей.
        Returns:
        bool: True, если водитель вернулся к работе, иначе False.
        """
        if self.on_lunch:
            self.resting_time += timedelta(minutes=1)
            if self.resting_time >= self.break_duration and bus_pool:
                drivers_on_lunch.remove(self)
                self.bus_for_driver(bus_pool)
                self.on_lunch = False
                self.all_rest = self.resting_time
                self.resting_time = timedelta(minutes=0)
                return True
            if self.resting_time > timedelta(hours=1):
                self.on_lunch = False
                self.all_rest = self.resting_time
                self.resting_time = timedelta(minutes=0)
                drivers_on_lunch.remove(self)
                self.end_of_the_day(active_drivers, finished_drivers, bus_pool)
            return False

    def drive_bus(
            self,
    ) -> bool:
        """
        Вызывает функцию move привязанного к водителю автобуса.


        Returns:
            bool: True, если автобус остановился, иначе False.
        """
        if self.bus and self.bus.move():
            return True
        return False

    def update_work_status(self) -> None:
        """
        Проверяет, сколько дней подряд отработал водитель, и обновляет статус возможности работать.
        """
        if self.shift_duration == DEFAULT_SHIFT_DURATION_12H:
            self.days_worked += 1
            if self.days_worked == 2:
                self.can_work_today = False
                self.day_off = DAY_OFF_DURATION_12H
                self.days_worked = 0

    def update_day_off(self) -> None:
        """
        Обновляет оставшееся время на выходном для 12-часового водителя.
        """
        if self.shift_duration == DEFAULT_SHIFT_DURATION_12H:
            if not self.can_work_today:
                self.day_off -= timedelta(minutes=1)
                if self.day_off <= timedelta(minutes=0):
                    self.can_work_today = True
                    self.day_off = DAY_OFF_DURATION_12H

    def end_of_the_day(
            self,
            active_drivers: List['BusDriver'],
            finished_drivers: List['BusDriver'],
            bus_pool: List['Bus']
    ) -> None:
        """
        Обновляет поля водителя после завершения смены.

        Args:
            active_drivers (List[BusDriver]): Список активных водителей.
            finished_drivers (List[BusDriver]): Список завершивших работу водителей.
            bus_pool (List[Bus]): Пул доступных автобусов.
        """
        self.working_time = timedelta(hours=0)
        self.on_lunch = False
        self.all_rest = timedelta(hours=0)
        if self.shift_duration == DEFAULT_SHIFT_DURATION_12H:
            self.daily_breaks = DAILY_BREAKS_12H
            self.update_work_status()
        else:
            self.daily_breaks = DAILY_BREAKS_8H
        if self.bus:
            self.release_bus_from_driver(bus_pool)
        finished_drivers.append(self)
        active_drivers.remove(self)

    def is_allowed_to_work(self, time_road: timedelta, current_time: timedelta) -> bool:
        """
        Проверяет, разрешено ли водителю работать в текущий момент.

        Args:
            time_road (timedelta): Время в пути.
            current_time (timedelta): Текущее время.

        Returns:
            bool: True, если разрешено работать, иначе False.
        """
        if self.bus:
            if self.bus.station in (START_STATION, N_OF_STATIONS):
                current_hour = ((current_time.days * MAX_HOUR) +
                                ((current_time.seconds + time_road.seconds) // SECONDS_IN_HOUR)) % MAX_HOUR
                if self.shift_duration == DEFAULT_SHIFT_DURATION_8H:
                    return (self.working_time + time_road) < self.shift_duration and \
                           (MIN_WORK_HOUR <= current_hour <= MAX_WORK_HOUR)
                return (self.working_time + time_road) < (self.shift_duration - timedelta(hours=1))
            return True
        return True


class BusStation:
    """
    Класс BusStation представляет автобусную остановку с уникальным идентификатором, направлением и списком ожидающих пассажиров.

    Attributes:
        station_id (int): Уникальный идентификатор остановки.
        direct (bool): Флаг, указывающий направление остановки.
    """

    def __init__(self, station_id: int, direct: bool) -> None:
        """
        Инициализирует объект BusStation.

        Args:
            station_id (int): Уникальный идентификатор остановки.
            direct (bool): Направление остановки.
        """
        self.station_id: int = station_id
        self.direct: bool = direct
