from db_importer import import_to_database
from plan_reader import read_from_file


def main() -> None:
    city_plan = read_from_file("city-plan.json")
    import_to_database(city_plan)


if __name__ == "__main__":
    main()
