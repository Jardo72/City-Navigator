# City Navigator - Data Importer

## Introduction

The Data Importer is a one-shot command-line utility that bootstraps the City Navigator database with a public transport network. It reads a JSON city plan file, derives the graph structure needed for journey-plan searches, and writes everything to a PostgreSQL database in a single atomic transaction.

In the Docker Compose setup the data importer runs automatically after the database is healthy and exits upon completion. All other services wait for it to finish before starting.

The importer is implemented in Python and uses [SQLAlchemy](https://www.sqlalchemy.org/) for database access.


## Usage

```bash
python main.py <input_file> <sqlalchemy_db_url>
```

| Argument | Description |
|---|---|
| `input_file` | Path to the JSON city plan file, e.g. `city-plan.json` |
| `sqlalchemy_db_url` | SQLAlchemy connection URL, e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |

During the import, each edge inserted is printed to stdout as an audit trail:

```
U1: Oberlaa <-> Neulaa (2 min)
U1: Neulaa <-> Alaudagasse (2 min)
...
```

On completion a summary is printed with the number of means of transport, stations, lines, and edges created.


## City Plan File Format

The city plan is a JSON file with the following structure:

```json
{
  "version": "1.0",
  "lines": [
    {
      "label": "U1",
      "meansOfTransport": "U-Bahn",
      "itinerary": [
        { "station": "Oberlaa",  "pointInTime": 0 },
        { "station": "Neulaa",   "pointInTime": 2 },
        { "station": "Karlsplatz", "pointInTime": 14 }
      ]
    }
  ]
}
```

`pointInTime` is the cumulative travel time in minutes from the first station of the line. The travel time between two consecutive stops is the difference of their `pointInTime` values.

### Bundled data: Vienna public transport

The file `city-plan.json` contains a simplified but realistic snapshot of Vienna's public transport network, suitable for demo and educational purposes. It covers 15 lines across four means of transport:

| Means of transport | Lines |
|---|---|
| U-Bahn (subway) | U1, U2, U3, U4, U6 |
| S-Bahn (commuter rail) | S1, S45 |
| Tram | 5, 18, 30 |
| Bus | 2A, 7A, 10A, 31A |

Station names are real Vienna locations. Several stations appear on multiple lines (e.g. Karlsplatz, Praterstern, Westbahnhof), forming the transfer points that make multi-line journey planning possible.


## What the Importer Creates

For each city plan the importer populates four database tables:

| Table | Content |
|---|---|
| `t_means_of_transport` | One row per distinct transport type (U-Bahn, S-Bahn, Tram, Bus) |
| `t_stations` | One row per unique station name across all lines |
| `t_lines` | One row per line, with references to its two terminal stops |
| `t_edges` | Two rows per consecutive station pair on each line (one in each direction) |

Edges are stored bidirectionally so that the Dijkstra algorithm in the Query Service can find paths in either direction without requiring the city plan to list both directions explicitly. The `distance_min` column on each edge holds the travel time in minutes between the two stations.

All primary keys are randomly generated UUIDs (`uuid4`).
