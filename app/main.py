from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from contextlib import contextmanager

from .database import get_db, engine, Base
from .models import Person
from .schemas import PersonCreate, PersonResponse, PersonUpdate


# 1. Создаем функцию lifespan (синхронную, так как у нас синхронный SQLAlchemy)
@contextmanager
def lifespan(app: FastAPI):
    # --- БЛОК СТАРТА (вместо on_event("startup")) ---
    # Создаем таблицы в БД при запуске приложения
    Base.metadata.create_all(bind=engine)
    # Здесь можно добавить логирование: print("Application started, DB tables checked.")

    yield  # Приложение работает

    # --- БЛОК ОСТАНОВКИ (вместо on_event("shutdown")) ---
    # Здесь обычно закрывают пулы соединений, но для SQLAlchemy SessionLocal
    # это делается в зависимости get_db, поэтому блок может быть пустым.
    # print("Application shutting down...")


# 2. Передаем lifespan в конструктор FastAPI
app = FastAPI(title="Lab1 Person API", version="1.0.0", lifespan=lifespan)


@app.get("/persons", response_model=List[PersonResponse])
def list_persons(db: Session = Depends(get_db)):
    return db.query(Person).all()


@app.get("/persons/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@app.post("/persons", status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    db_person = Person(name=person.name, age=person.age)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    from fastapi.responses import Response
    location = f"/persons/{db_person.id}"
    return Response(status_code=201, headers={"Location": location})


@app.patch("/persons/{person_id}")
def update_person(person_id: int, person_update: PersonUpdate, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    if person_update.name is not None:
        person.name = person_update.name
    if person_update.age is not None:
        person.age = person_update.age

    db.commit()
    db.refresh(person)
    return PersonResponse.model_validate(person)


@app.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return None
