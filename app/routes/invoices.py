from fastapi import APIRouter, HTTPException
from app.models import InvoiceCreate
from app import crud

#from app.crud import create_invoice as insert_invoice  # enamed to avoid conflict
#import logging
#logger = logging.getLogger("uvicorn.info")

router = APIRouter(prefix="/invoices", tags=["Invoices"])



#@router.post("/")
#def create_invoice_endpoint(invoice: InvoiceCreate):
#logger.info("🧾 IN INVOICES BEFORE GOING TO CRUD")


@router.post("/")
def create_invoice_endpoint(invoice: InvoiceCreate):  # use InvoiceCreate
    print("IN INVOICES BEFORE GOING TO CRUD")
    try:
        invoice_data = crud.create_invoice(invoice)  # ✅ call with actual data
        invoice_id = invoice_data["id"]  # ✅ get the ID from returned dict
        print("INVOICE_ID IN INVOICES.PY = ", invoice_id)
        print("✅ Invoice saved with ID:", invoice_id)
        return {"invoice_id": invoice_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

