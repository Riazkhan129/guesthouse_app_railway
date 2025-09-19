from fastapi import APIRouter, HTTPException, Request
from app.models import InvoiceCreate
from app import crud

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.post("/")
def create_invoice_endpoint(request: Request, invoice: InvoiceCreate):  # use InvoiceCreate
    print("IN INVOICES BEFORE GOING TO CRUD")
    try:
        client_id = get_client_id(request)
        if not client_id:
            raise HTTPException(status_code=400, detail="Missing client_id")
        invoice_data = crud.create_invoice(client_id, invoice)  # ✅ call with actual data
        invoice_id = invoice_data["id"]  # ✅ get the ID from returned dict
        print("INVOICE_ID IN INVOICES.PY = ", invoice_id)
        print("✅ Invoice saved with ID:", invoice_id)
        return {"invoice_id": invoice_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

