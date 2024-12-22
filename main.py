from simulation import simulate_time
from to_excel import excel_schedule
from constants import *


def main():
    # Запуск симуляции
    df = simulate_time(
        simulation_duration=SIMULATION_DURATION,
        n_of_stations=N_OF_STATIONS,
        n_of_buses=N_OF_BUS,
        n_of_drivers_eight_shift=N_OF_DRIVERS_EIGHT_SHIFT,
        n_of_drivers_twelve_shift=N_OF_DRIVERS_TWELVE_SHIFT
    )

    # Определение имени выходного файла
    output_file = "drivers_schedule.xlsx"

    # Сохранение результатов в Excel
    excel_schedule(df, output_file)

    # Вывод информации о завершении
    print("Симуляция завершена.")
    print(f"Расписание сохранено в файл: {output_file}")
    print(f"Всего водителей задействовано: {len(df.columns) - 1}")


if __name__ == "__main__":
    main()
