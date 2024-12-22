from datetime import timedelta
from models import Bus, BusDriver, BusStation
from typing import List, Tuple
import random


def generate_unique_names(count: int) -> List[str]:
    """
    Генерирует уникальные имена из предопределенного списка.

    Args:
        count (int): Количество уникальных имен для генерации.

    Returns:
        List[str]: Список уникальных имен.

    Raises:
        ValueError: Если запрашиваемое количество имен превышает доступное количество уникальных имен.
    """
    all_names = [
        "Санёк", "Петя", "Ванёк", "Колян", "Серёга", "Андрюха", "Диман", "Женёк", "Кирюха",
        "Егорка", "Миха", "Глебыч", "Макс", "Владос", "Олежа", "Ромка", "Игорь", "Сеня",
        "Тимоха", "Матвей", "Никитос", "Гриша", "Антоша", "Лёха", "Даня", "Ярик", "Вован",
        "Славян", "Стасян", "Федя", "Лёня", "Витя", "Жора", "Костян", "Тоха",
        "Гена", "Пашка", "Артём", "Стёпа", "Захар", "Евгений", "Боря", "Валёк", "Виталька",
        "Мишаня", "Гарик", "Саша", "Виктор", "Толя", "Юра", "Саня", "Григорий", "Павел",
        "Назар", "Руслан", "Денис", "Филипп", "Кирилл", "Эдик", "Илья", "Дамир", "Рустам",
        "Айдар", "Амир", "Серый", "Коляныч", "Игорёк", "Семёныч", "Богдан", "Дим Димыч",
        "Марк", "Прохор", "Родя", "Тёма", "Виталя", "Ян", "Иван", "Тимур", "Савва", "Платон",
        "Клим", "Лавр", "Васёк", "Петруха", "Захарыч", "Гришка", "Макарыч", "Филиппыч",
        "Гаврил", "Яков", "Анатолий", "Валера", "Лев", "Мартын",
        "Кеша", "Мирон", "Эльдар", "Ратмир", "Марат", "Геннадий", "Адам", "Ренат", "Леонид",
        "Аркаша", "Трофим", "Вадим", "Всеволод", "Борислав", "Светозар", "Родион", "Юрий"
    ]
    if count > len(all_names):
        raise ValueError("Запрашиваемое количество имен превышает доступное количество уникальных имен.")
    random.shuffle(all_names)
    return all_names[:count]


def create_stations(n_of_stations: int) -> List['BusStation']:
    """
    Создает список станций для прямого и обратного направления.

    Args:
        n_of_stations (int): Количество станций.

    Returns:
        List[BusStation]: Список станций.
    """
    stations = []
    for i in range(1, n_of_stations + 1):
        stations.append(BusStation(station_id=i, direct=True))
        stations.append(BusStation(station_id=i, direct=False))
    return stations


def create_buses(n_of_bus: int) -> List[Bus]:
    """
    Создает списки автобусов для прямого и обратного направления.

    Args:
        n_of_bus (int): Количество автобусов

    Returns:
        Tuple[List[Bus], List[Bus]]: Кортеж списков прямых и обратных автобусов.
    """
    direct_buses = [Bus(number=i, direct=True) for i in range(n_of_bus)]
    return direct_buses


def create_drivers(
        n_of_drivers_eight_shift: int,
        n_of_drivers_twelve_shift: int,
        driver_names: List[str],
) -> List[BusDriver]:
    """
    Создает списки водителей для прямого и обратного направления.

    Args:
        n_of_drivers_eight_shift (int): Количество 8-часовых водителей для прямого направления.
        n_of_drivers_twelve_shift (int): Количество 12-часовых водителей для прямого направления.
        driver_names (List[str]): Список уникальных имен для водителей.

    Returns:
        List[BusDriver]: Cписок водителей
    """
    drivers: List['BusDriver'] = []
    name_index = 0

    for _ in range(n_of_drivers_eight_shift):
        drivers.append(BusDriver(
            name=driver_names[name_index],
            shift_duration=timedelta(hours=8),
            bus=None
        ))
        name_index += 1

    for _ in range(n_of_drivers_twelve_shift):
        drivers.append(BusDriver(
            name=driver_names[name_index],
            shift_duration=timedelta(hours=12),
            bus=None
        ))
        name_index += 1

    return drivers


def initialize(
        n_of_stations: int,
        n_of_bus: int,
        n_of_drivers_eight_shift: int,
        n_of_drivers_twelve_shift: int,
) -> Tuple[List['BusStation'], List['Bus'], List['BusDriver']]:
    """
    Инициализирует станции, автобусы и водителей.

    Args:
        n_of_stations (int): Количество станций.
        n_of_bus (int): Количество автобусов
        n_of_drivers_eight_shift (int): Количество 8-часовых водителей
        n_of_drivers_twelve_shift (int): Количество 12-часовых водителей

    Returns:
        Tuple[List[BusStation], List[Bus], List[Bus], List[BusDriver], List[BusDriver]]:
            Кортеж, содержащий списки станций, прямых автобусов, обратных автобусов,
            водителей прямого направления и водителей обратного направления.
    """
    stations = create_stations(n_of_stations)
    buses = create_buses(n_of_bus)
    driver_names = generate_unique_names(
        n_of_drivers_eight_shift +
        n_of_drivers_twelve_shift
    )
    drivers = create_drivers(
        n_of_drivers_eight_shift,
        n_of_drivers_twelve_shift,
        driver_names
    )
    return stations, buses, drivers
