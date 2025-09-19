from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class Client_keysBase(BaseModel):
    encryption_key: str

class Client_keysGet(BaseModel):
    encryption_key: str

# --------- User ---------
class UserBase(BaseModel):
    name:  str
    username: str
    password: str
    role: str


class UserCreate(UserBase):
    name:  str
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    user_id: int
    name: str
    username: str
    password: str
    role: str

class UserUpdate(BaseModel):
    name: str
    role: str
    password: Optional[str] = None

    

# --------- Room ---------
class RoomBase(BaseModel):
    room_number: str
    type: str
    price: float
    status: str
    notes: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomIn(BaseModel):
    room_number: str
    type: str
    price: float
    status: str
    notes: Optional[str] = None

class RoomOut(BaseModel):
    room_number: str
    type: str
    price: float
    status: str
    notes: Optional[str] = None
    

# --------- Guest ---------
# ---------- Shared Base ----------
class GuestBase(BaseModel):
    nic_passport_number: str
    name: str
    contact: str
    email: Optional[EmailStr] = None
    address: str
    nationality: Optional[str] = None
    emergency_contact: Optional[str] = None
    guest_type: Optional[str] = None

# ---------- Create ----------
class GuestCreate(GuestBase):
    pass

# ---------- Input (for Update/Search) ----------
class GuestIn(GuestBase):
    pass

# ---------- Output ----------
class GuestOut(GuestBase):
    pass

# ---------- Update ----------
class GuestUpdate(BaseModel):
    name: Optional[str]
    contact: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    nationality: Optional[str]
    emergency_contact: Optional[str]
    guest_type: Optional[str]


# ---------- Booking Response ----------
class BookingIDResponse(BaseModel):
    booking_id: int

# --------- Booking ---------
# Booking Models

class BookingBase(BaseModel):
    booking_id: int
    nic_passport_number: str
    room_number: Optional[str]  # allow None for future bookings
    checkin_date: str
    checkout_date: str
    status: str
    notes: Optional[str] = None
    actual_checkin_time: Optional[str] = None
    advance_payment: Optional[int] = None
    actual_checkout_date: Optional[str] = None
    total_payment: Optional[int] = None
    invoice_id: Optional[int] = None

class BookingUpdate(BaseModel):
    status: str
    actual_checkout_date: Optional[str] = None
    total_payment: Optional[int] = None
    invoice_id: int

class BookingCreate(BaseModel):
    nic_passport_number: str
    room_number: Optional[str]  # allow None for future bookings
    checkin_date: str
    checkout_date: str
    status: str
    notes: Optional[str] = None
    advance_payment: Optional[int]
    total_payment: Optional[int]
    booked_rooms: Optional[int]
    total_rooms: Optional[int]

class BookingOut(BaseModel):
    booking_id: int
    nic_passport_number: str
    room_number: Optional[str]  # allow None for future bookings
    #room_number: str
    checkin_date: str
    checkout_date: str
    status: str
    notes: Optional[str]
    actual_checkin_time: Optional[str] = None
    advance_payment: Optional[int] = None
    actual_checkout_date: Optional[str] = None
    total_payment: Optional[int] = None

class BookingOutCheckIn(BaseModel):
    booking_id: int
    nic_passport_number: str
    room_number: Optional[str]  # allow None for future bookings
    #room_number: str
    checkin_date: str
    checkout_date: str
    status: str
    notes: Optional[str]
    actual_checkin_time: Optional[str] = None
    advance_payment: Optional[int] = None
    actual_checkout_time: Optional[str] = None
    total_payment: Optional[int] = None
    guest_name: Optional[str]

class BookingSummary(BaseModel):
    booking_id: int
    room_number: Optional[str]
    checkin_date: str
    checkout_date: str
    status: str

    
class CheckinData(BaseModel):
    room_number: str
    checkout_date: str
    actual_checkin_time: str
    advance_payment: float
    status: str
    

class BookingResponse(BaseModel):
    booking_id: int

#from pydantic import BaseModel

class CancelBookingRequest(BaseModel):
    #room_number: str
    room_number: Optional[str]  # allow None for future bookings


# --------- Invoice ---------
class InvoiceBase(BaseModel):
    booking_id: int
    guest_nic: str
    guest_name: str
    room_number: str
    room_price: float
    checkin_date: str
    checkout_date: str
    total_nights: int
    room_charges: float
    laundry: float
    meals: float
    damages: float
    total_amount: float
    

class InvoiceCreate(InvoiceBase):
    pass


class InvoiceOut(InvoiceBase):
    invoice_id: int

# --------- Billing ---------

from pydantic import BaseModel
from datetime import date

class BillingIn(BaseModel):
    booking_id: int
    amount: float
    date: str  # Or `date` if using datetime.date

class BillingOut(BillingIn):
    id: int

# --------- Expense ---------
from pydantic import BaseModel
from typing import Optional

# --------- Expense Models ---------
class ExpenseBase(BaseModel):
    title: str
    amount: float
    category: str = "Salary"
    notes: Optional[str] = None
    date: str

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseOut(ExpenseBase):
    id: int
    
