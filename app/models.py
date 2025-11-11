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

# schemas.py
#from pydantic import BaseModel

class ExpenseCategoryBase(BaseModel):
    category_name: str
    category_active: bool = True

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategoryUpdate(ExpenseCategoryBase):
    pass
    

class ExpenseCategoryOut(ExpenseCategoryBase):
    id: int


    class Config:
        orm_mode = True

#----------------

class ExpenseItemBase(BaseModel):
    category_id: int
    expense_name: str
    default_price: int
    unit: str
    is_activated: bool = True

class ExpenseItemCreate(ExpenseItemBase):
    pass

class ExpenseItemUpdate(ExpenseItemBase):
    pass

class ExpenseItemOut(ExpenseItemBase):
    expense_item_id: int
    created: str

    class Config:
        orm_mode = True

#---------------- Room Service --------------

class RoomServiceRequestIn(BaseModel):
    room_id: str
    nic_passport_number: str
    category_id: int
    expense_item_id: int
    quantity: int
    unit_price: int
    total_price: int
    notes: Optional[str] = None
    requested_at: Optional[str] = None
    Status: str
    booking_id: int
    
    

class RoomServiceRequestOut(RoomServiceRequestIn):
    id: int
    total_price: int

class RoomServiceSummaryOut(BaseModel):
    category_name: str
    total_amount: int

class RoomServiceItemDetail(BaseModel):
    category_name: str
    expense_name: str
    total_price: int

class RoomServiceItemGroupByDate(BaseModel):
    date: str
    items: list[RoomServiceItemDetail]

    

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
    corporate_name: Optional[str] = None
    corporate_contact_person: Optional[str] = None
    corporate_address: Optional[str] = None

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
    corporate_name: Optional[str] = None
    corporate_contact_person: Optional[str] = None
    corporate_address: Optional[str] = None


# ---------- Booking Response ----------
class BookingIDResponse(BaseModel):
    booking_id: int

# --------- Booking ---------
# Booking Models

class BookingBase(BaseModel):
    booking_id: int
    nic_passport_number: str
    checkin_date: str
    checkout_date: str
    status: str
    room_number: Optional[str]
    room_type: str
    room_rate: int
    notes: Optional[str] = None
    actual_checkin_time: Optional[str] = None
    companions: int
    advance_payment: Optional[int] = None
    actual_checkout_date: Optional[str] = None
    total_payment: Optional[int] = None
    corporate_name: Optional[str] = None
    payment_mode: Optional[str] = None
    profession: Optional[str] = None
    visit_purpose: Optional[str] = None
    payment_status: Optional[str] = None
    invoice_id: Optional[int] = None

class BookingUpdate(BaseModel):
    status: str
    actual_checkout_time: Optional[str] = None
    total_payment: Optional[int] = None
    invoice_id: Optional[int]

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
    corporate_name: Optional[str] = None

class BookingOut(BaseModel):
    booking_id: int
    nic_passport_number: str
    room_number: Optional[str]  # allow None for future bookings
    room_type: Optional[str]
    room_rate: Optional[int]
    #room_number: str
    checkin_date: str
    checkout_date: str
    status: str
    notes: Optional[str]
    actual_checkin_time: Optional[str] = None
    companions: Optional[int]
    advance_payment: Optional[int] = None
    actual_checkout_time: Optional[str] = None
    total_payment: Optional[int] = None
    corporate_name: Optional[str] = None
    
    

class BookingOutCheckIn(BaseModel):
    booking_id: int
    nic_passport_number: str
    checkin_date: str
    checkout_date: str    
    status: str
    room_number: Optional[str]
    room_type: Optional[str]
    room_rate: Optional[int]
    notes: Optional[str]
    actual_checkin_time: Optional[str] = None
    companions: Optional[int]
    advance_payment: Optional[int] = None
    actual_checkout_date: Optional[str] = None
    total_payment: Optional[int] = None
    guest_name: Optional[str]
    corporate_name: Optional[str] = None
    


class BookingSummary(BaseModel):
    booking_id: int
    room_number: Optional[str]
    checkin_date: str
    checkout_date: str
    status: str


class CheckinData(BaseModel):
    room_number: str
    room_type: str
    room_rate: int
    companions: int
    mode_of_payment: str
    profession: str
    purpose_of_visit: str
    actual_checkin_time: str
    checkout_date: str
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

# --------- Expense Models ---------
from pydantic import BaseModel
from typing import Optional

class ExpenseBase(BaseModel):
    category_id: int
    expense_item_id: int
    amount: float
    notes: Optional[str] = None
    timestamp: str
    date: str

class ExpenseCreate(ExpenseBase):
    category_id: int
    expense_item_id: int
    amount: float
    notes: Optional[str] = None
    timestamp: str
    date: str

class ExpenseOut(ExpenseBase):
    expense_id: int
    category_id: int
    category_name: str
    expense_item_id: int
    expense_name: str
    amount: float
    notes: Optional[str] = None
    timestamp: str
    date: str

class ExpenseUpdate (BaseModel):
    amount: float
    notes: Optional[str] = None
    timestamp: str
    date: str
