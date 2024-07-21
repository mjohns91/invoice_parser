import pdfquery
import os
import re

# ---bbox coords (x0, y0, x1, y1)---
invoice_date: tuple = (394.56, 568.8, 450, 581.76)
invoice_number: tuple = (411.84, 583.2, 494.64, 601.92)

def is_pdf(file: str) -> bool:
    """Returns true if file ends with '.pdf' and false if any other ending is found.
    
    """
    if file.endswith(".pdf"):
        return True
    else:
        return False
    

def load_and_parse_pdf(src_path: str, file: str, data: dict) -> dict:
    """Return a dict containing invoice date parts and invoice number.

    """
    # Create full file path for passed pdf
    pdf_path = os.path.join(src_path, file)
    current_pdf = pdfquery.PDFQuery(pdf_path)
    
    # Open pdf
    current_pdf.load()

    # Get date from invoice and save parts into list [YYYY, MM, DD]
    date_string = current_pdf.pq(\
        'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
            % (invoice_date[0], invoice_date[1], invoice_date[2], invoice_date[3])).text()
    
    # Use regular expression to find year, month, day
    date_string = re.findall('\\d+', date_string)
    data["inv_date"] = date_string
    
    # Get invoice number
    number_string = current_pdf.pq(\
        'LTTextLineHorizontal:overlaps_bbox("%d, %d, %d, %d")' \
            % (invoice_number[0], invoice_number[1], invoice_number[2], invoice_number[3])).text()
    
    # Use regular expression to find invoice number
    numbers = re.findall('\\d+', number_string)
    data["inv_number"] = numbers[0]

    # Close pdf
    current_pdf.file.close()

    return data