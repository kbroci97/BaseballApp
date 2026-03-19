#!/usr/bin/env python3
"""Create a SQLite database from the provided CSV files.

This script reads the following CSV files from the repo root:
  - people.csv
  - teams.csv
  - batting.csv

It then creates a `baseball.db` SQLite database with three tables:
  - people (PK: playerID)
  - teams (PK: yearID, teamID)
  - batting (PK: playerID, yearID, stint)

The schema enforces the requested foreign keys:
  - batting.playerID -> people.playerID
  - batting.(yearID, teamID) -> teams.(yearID, teamID)

Usage:
    python create_sqlite_db.py

Output:
    baseball.db
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "baseball.db"


def _load_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Load a CSV file with sane defaults for missing values."""
    return pd.read_csv(path, keep_default_na=True, na_values=[""], **kwargs)


def _coerce_ints(df: pd.DataFrame, int_columns: list[str]) -> pd.DataFrame:
    """Coerce columns to nullable integers (Int64) and keep missing values as None."""
    for col in int_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    # Convert pandas NA / NaN to None for sqlite inserts.
    return df.where(pd.notnull(df), None)


def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # Enable foreign keys for this connection.
    cur.execute("PRAGMA foreign_keys = ON;")

    # Drop existing tables (safe to re-run this script).
    cur.executescript(
        """
        DROP TABLE IF EXISTS batting;
        DROP TABLE IF EXISTS teams;
        DROP TABLE IF EXISTS people;
        """
    )

    cur.executescript(
        """
        CREATE TABLE people (
            playerID TEXT PRIMARY KEY,
            ID INTEGER,
            birthYear INTEGER,
            birthMonth INTEGER,
            birthDay INTEGER,
            birthCity TEXT,
            birthCountry TEXT,
            birthState TEXT,
            deathYear INTEGER,
            deathMonth INTEGER,
            deathDay INTEGER,
            deathCountry TEXT,
            deathState TEXT,
            deathCity TEXT,
            nameFirst TEXT,
            nameLast TEXT,
            nameGiven TEXT,
            weight INTEGER,
            height INTEGER,
            bats TEXT,
            throws TEXT,
            debut TEXT,
            bbrefID TEXT,
            finalGame TEXT,
            retroID TEXT
        );

        CREATE TABLE teams (
            yearID INTEGER,
            lgID TEXT,
            teamID TEXT,
            franchID TEXT,
            divID TEXT,
            Rank INTEGER,
            G INTEGER,
            Ghome INTEGER,
            W INTEGER,
            L INTEGER,
            DivWin TEXT,
            WCWin TEXT,
            LgWin TEXT,
            WSWin TEXT,
            R INTEGER,
            AB INTEGER,
            H INTEGER,
            "2B" INTEGER,
            "3B" INTEGER,
            HR INTEGER,
            BB INTEGER,
            SO INTEGER,
            SB INTEGER,
            CS INTEGER,
            HBP INTEGER,
            SF INTEGER,
            RA INTEGER,
            ER INTEGER,
            ERA REAL,
            CG INTEGER,
            SHO INTEGER,
            SV INTEGER,
            IPouts INTEGER,
            HA INTEGER,
            HRA INTEGER,
            BBA INTEGER,
            SOA INTEGER,
            E INTEGER,
            DP INTEGER,
            FP REAL,
            name TEXT,
            park TEXT,
            attendance INTEGER,
            BPF INTEGER,
            PPF INTEGER,
            teamIDBR TEXT,
            teamIDlahman45 TEXT,
            teamIDretro TEXT,
            PRIMARY KEY (yearID, teamID)
        );

        CREATE TABLE batting (
            playerID TEXT,
            yearID INTEGER,
            stint INTEGER,
            teamID TEXT,
            lgID TEXT,
            G INTEGER,
            AB INTEGER,
            R INTEGER,
            H INTEGER,
            "2B" INTEGER,
            "3B" INTEGER,
            HR INTEGER,
            RBI INTEGER,
            SB INTEGER,
            CS INTEGER,
            BB INTEGER,
            SO INTEGER,
            IBB INTEGER,
            HBP INTEGER,
            SH INTEGER,
            SF INTEGER,
            GIDP INTEGER,
            PRIMARY KEY (playerID, yearID, stint),
            FOREIGN KEY (playerID) REFERENCES people(playerID),
            FOREIGN KEY (yearID, teamID) REFERENCES teams(yearID, teamID)
        );
        """
    )
    conn.commit()


def main() -> None:
    print("Creating sqlite database at", DB_PATH)

    people_csv = ROOT / "people.csv"
    teams_csv = ROOT / "teams.csv"
    batting_csv = ROOT / "batting.csv"

    if not (people_csv.exists() and teams_csv.exists() and batting_csv.exists()):
        raise FileNotFoundError(
            "Expected people.csv, teams.csv, and batting.csv in the repository root."
        )

    conn = sqlite3.connect(DB_PATH)

    try:
        create_schema(conn)

        # Load each dataset using pandas and coerce types.
        people = _load_csv(people_csv, dtype=str)
        people = _coerce_ints(
            people,
            [
                "ID",
                "birthYear",
                "birthMonth",
                "birthDay",
                "deathYear",
                "deathMonth",
                "deathDay",
                "weight",
                "height",
            ],
        )

        teams = _load_csv(teams_csv, dtype=str)
        teams = _coerce_ints(
            teams,
            [
                "yearID",
                "Rank",
                "G",
                "Ghome",
                "W",
                "L",
                "R",
                "AB",
                "H",
                "2B",
                "3B",
                "HR",
                "BB",
                "SO",
                "SB",
                "CS",
                "HBP",
                "SF",
                "RA",
                "ER",
                "CG",
                "SHO",
                "SV",
                "IPouts",
                "HA",
                "HRA",
                "BBA",
                "SOA",
                "E",
                "DP",
                "attendance",
                "BPF",
                "PPF",
            ],
        )

        batting = _load_csv(batting_csv, dtype=str)
        batting = _coerce_ints(
            batting,
            [
                "yearID",
                "stint",
                "G",
                "AB",
                "R",
                "H",
                "2B",
                "3B",
                "HR",
                "RBI",
                "SB",
                "CS",
                "BB",
                "SO",
                "IBB",
                "HBP",
                "SH",
                "SF",
                "GIDP",
            ],
        )

        people.to_sql("people", conn, if_exists="append", index=False)
        teams.to_sql("teams", conn, if_exists="append", index=False)
        batting.to_sql("batting", conn, if_exists="append", index=False)

        print("✅ Created", DB_PATH, "with tables: people, teams, batting")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
