from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.models import Contact, Profile, CheckIn
from api.schemas import CheckInCreate, ProfileCreate
from api.utils.twilio_helpers import send_otp
from api.utils.printer_helpers import print_name_tag

router = APIRouter()

@router.post("/check-in")
async def check_in(phone_number: str, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.phone_number == phone_number).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Send OTP
    otp = send_otp(phone_number)
    
    return {"message": "OTP sent", "contact_id": contact.contact_id}

@router.post("/check-in/verify")
async def verify_check_in(contact_id: int, otp: str, db: Session = Depends(get_db)):
    # Verify OTP (implement this logic)
    if not verify_otp(contact_id, otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    contact = db.query(Contact).filter(Contact.contact_id == contact_id).first()
    profile = db.query(Profile).filter(Profile.contact_id == contact_id).first()
    
    if not profile or not profile.is_complete():
        return {"message": "Profile incomplete", "contact_id": contact_id}
    
    # Create check-in record
    check_in = CheckIn(contact_id=contact_id)
    db.add(check_in)
    db.commit()
    
    # Print name tag
    print_name_tag(contact.name, profile.bio)
    
    return {"message": "Check-in successful", "check_in_id": check_in.check_in_id}

@router.post("/check-in/complete-profile")
async def complete_profile(profile_data: ProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.contact_id == profile_data.contact_id).first()
    if not profile:
        profile = Profile(**profile_data.dict())
        db.add(profile)
    else:
        for key, value in profile_data.dict().items():
            setattr(profile, key, value)
    
    db.commit()
    
    # Print name tag
    contact = db.query(Contact).filter(Contact.contact_id == profile_data.contact_id).first()
    print_name_tag(contact.name, profile.bio)
    
    return {"message": "Profile completed and name tag printed"}