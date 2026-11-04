from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import Base, Person
from .schemas import PersonCreate, PersonResponse, PersonUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Lab1 Person API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/api/v1/persons", response_model=List[PersonResponse])
def list_persons(db: Session = Depends(get_db)):
    return db.query(Person).all()


@app.get("/api/v1/persons/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person


@app.post("/api/v1/persons", status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    db_person = Person(**person.model_dump())

    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    return Response(
        status_code=201,
        headers={"Location": f"/api/v1/persons/{db_person.id}"}
    )


@app.patch("/api/v1/persons/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: Session = Depends(get_db)
):
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    updates = person_update.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(person, key, value)

    db.commit()
    db.refresh(person)

    return person


@app.delete(
    "/api/v1/persons/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    db.delete(person)
    db.commit()

    return Response(status_code=204)
