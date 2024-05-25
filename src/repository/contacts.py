from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.datebase.models import Contacts
from src.schemas import ContactCreate, ContactUpdate


async def get_contacts(skip: int, limit: int, db: Session):
    return db.query(Contacts).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session):
    return db.query(Contacts).filter(Contacts.id == contact_id).first()


async def create_contact(body: ContactCreate, db: Session):
    contact = Contacts(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: Session):
    contact = db.query(Contacts).filter(Contacts.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, db: Session):
    contact = db.query(Contacts).filter(Contacts.id == contact_id).first()
    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional = body.additional
        db.commit()
    return contact


async def get_birthdays(db: Session):
    today = datetime.today()
    offset = today + timedelta(days=7)
    result = db.query(Contacts).filter(Contacts.birthday.between(today, offset)).all()
    return result


async def search_contacts(query: str, db: Session):
    result = db.query(Contacts).filter(
            (Contacts.name.ilike(f"%{query}%"))|
            (Contacts.lastname.ilike(f"%{query}%"))|
            (Contacts.email.ilike(f"%{query}%"))
        ).all()
    return result


