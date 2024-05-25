from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.datebase.db import get_db
from src.schemas import Contact, ContactCreate, ContactUpdate
from src.repository import contacts as repository_contacts


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.post("/", response_model=Contact)
async def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)


@router.get("/", response_model=List[Contact])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await repository_contacts.get_contacts(skip, limit, db)


@router.get("/{contact_id}", response_model=Contact)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=Contact)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/birthdays/", response_model=List[Contact])
async def get_birthdays(db: Session = Depends(get_db)):
    return await repository_contacts.get_birthdays(db)


@router.get("/search/", response_model=List[Contact])
async def search_contatcs(query, db: Session = Depends(get_db)):
    return await repository_contacts.search_contacts(query, db)