# BaseballApp

This repository contains baseball data in CSV format and a small script to load the data into an SQLite database.

## Creating the database

Run the included script to create `baseball.db` with three tables:

- `people` (PK: `playerID`)
- `teams` (PK: `yearID`, `teamID`)
- `batting` (PK: `playerID`, `yearID`, `stint`, FKs to `people` and `teams`)

```bash
python create_sqlite_db.py
```

The resulting file is written to `baseball.db` in the repository root.
