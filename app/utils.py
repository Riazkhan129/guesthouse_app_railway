import os
from xhtml2pdf import pisa

# --- 1. Render Invoice HTML ---
def render_invoice_html(guest, room_number, checkin_date, billing, room_price):
    checkout_date = billing.get("checkout_date", "Today")
    return f"""
    <div style='font-family:Arial; padding:20px; max-width:600px; margin:auto; border:1px solid #ddd;'>
        <h2 style='text-align:center;'>Guest House Invoice</h2>
        <hr>
        <p><strong>Guest Name:</strong> {guest['name']}</p>
        <p><strong>Room Number:</strong> {room_number}</p>
        <p><strong>Check-in Date:</strong> {checkin_date}</p>
        <p><strong>Checkout Date:</strong> {checkout_date}</p>
        <p><strong>Nights Stayed:</strong> {billing['nights']}</p>
        <hr>
        <h4>Charges</h4>
        <p>Room Rate: Rs. {room_price}</p>
        <p>Room Charges: Rs. {billing['room_charges']}</p>
        <p>Laundry: Rs. {billing['laundry']}</p>
        <p>Meals: Rs. {billing['meals']}</p>
        <p>Damages: Rs. {billing['damages']}</p>
        <hr>
        <h3>Total Amount: Rs. {billing['total_amount']}</h3>
        <p style='text-align:center;'>Thank you for staying with us!</p>
    </div>
    """

# --- 2. Convert HTML to PDF ---
def html_to_pdf(source_html, output_filename):
    with open(output_filename, "w+b") as result_file:
        pisa.CreatePDF(src=source_html, dest=result_file)
    return output_filename

# --- 3. Send Invoice via Email ---
import smtplib
from email.message import EmailMessage

def send_invoice_email(to_email, attachment_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Guest House Invoice"
        msg["From"] = "you@example.com"   # Replace with your email
        msg["To"] = to_email
        msg.set_content("Please find your invoice attached.")

        with open(attachment_path, "rb") as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=os.path.basename(attachment_path))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("you@example.com", "your-password")  # Replace securely
            server.send_message(msg)

        return True
    except Exception as e:
        print("Email sending error:", e)
        return False
