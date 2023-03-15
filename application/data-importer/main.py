from db_importer import ImportSummary
from db_importer import import_to_database
from plan_reader import read_from_file


def print_summary(import_summary: ImportSummary) -> None:
    print(f"Number of imported means of transport: {import_summary.means_of_transport_count}")
    print(f"Number of imported stations:           {import_summary.station_count}")
    print(f"Number of imported lines:              {import_summary.line_count}")
    print(f"Number of imported edges:              {import_summary.edge_count}")


def main() -> None:
    city_plan = read_from_file("city-plan.json")
    import_summary = import_to_database(city_plan)
    print_summary(import_summary)


if __name__ == "__main__":
    main()
