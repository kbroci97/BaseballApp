from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models import Batting, Teams, People, engine
from sqlmodel import Session, select

app = FastAPI()

@app.get("/years")
def get_years():
    with Session(engine) as session:
        years = session.exec(select(Batting.yearID).distinct().order_by(Batting.yearID)).all()
        return {"years": years}

@app.get("/teams")
def get_teams(year: int):
    with Session(engine) as session:
        teams = session.exec(select(Teams).where(Teams.yearID == year)).all()
        return {"teams": teams}

app.mount("/", StaticFiles(directory="static", html=True), name="static")