import csv
import io
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def generate_csv(queryset, headers, fields):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    
    for obj in queryset:
        row = [getattr(obj, field) for field in fields]
        writer.writerow(row)
    
    return output.getvalue()

def generate_excel(queryset, headers, fields):
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    
    for obj in queryset:
        row = [getattr(obj, field) for field in fields]
        ws.append(row)
    
    wb.save(output)
    return output.getvalue()

def generate_pdf(queryset, headers, fields):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    data = [headers]
    for obj in queryset:
        row = [str(getattr(obj, field)) for field in fields]
        data.append(row)
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return buffer.getvalue()
