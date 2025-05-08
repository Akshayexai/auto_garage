from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Vehicle, Part, Bill
from .forms import VehicleForm, PartForm, BillForm
from .export_utils import generate_csv, generate_excel, generate_pdf
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
import xlwt
from datetime import datetime


def home(request):
    total_vehicles = Vehicle.objects.count()
    total_parts = Part.objects.count()
    total_bills = Bill.objects.count()
    recent_bills = Bill.objects.order_by('-created_at')[:5]
    low_stock_parts = Part.objects.filter(quantity__lt=10)
    
    context = {
        'total_vehicles': total_vehicles,
        'total_parts': total_parts,
        'total_bills': total_bills,
        'recent_bills': recent_bills,
        'low_stock_parts': low_stock_parts
    }
    return render(request, 'inventory/home.html', context)

def vehicle_list(request):
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    vehicles = Vehicle.objects.all().order_by('-created_at')
    parts = Part.objects.all()  # Changed to show all parts
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.save()  # Save vehicle first
            
            parts_used = request.POST.getlist('parts_used')
            parts_valid = True
            
            # Validate parts availability
            for part_id in parts_used:
                part = Part.objects.get(id=part_id)
                if part.quantity <= 0:
                    parts_valid = False
                    messages.error(request, f'Part {part.name} is out of stock!')
                    break
            
            if parts_valid:
                # Deduct parts quantity
                for part_id in parts_used:
                    part = Part.objects.get(id=part_id)
                    part.quantity -= 1
                    part.save()
                
                vehicle.parts_used.set(parts_used)
                messages.success(request, 'Vehicle added successfully!')
                return redirect('vehicle_list')
            else:
                vehicle.delete()  # Delete vehicle if parts validation fails
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        form = VehicleForm()
    
    context = {
        'vehicles': vehicles,
        'form': form,
        'parts': parts,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'inventory/vehicle_list.html', context)

def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            old_parts = set(vehicle.parts_used.all().values_list('id', flat=True))
            new_parts = set(map(int, request.POST.getlist('parts_used')))
            
            for part_id in new_parts - old_parts:
                part = Part.objects.get(id=part_id)
                if part.quantity <= 0:
                    messages.error(request, f'Part {part.name} is out of stock!')
                    return redirect('edit_vehicle', pk=pk)
            
            parts_to_return = old_parts - new_parts
            for part_id in parts_to_return:
                part = Part.objects.get(id=part_id)
                part.quantity += 1
                part.save()
            
            parts_to_deduct = new_parts - old_parts
            for part_id in parts_to_deduct:
                part = Part.objects.get(id=part_id)
                part.quantity -= 1
                part.save()
            
            vehicle = form.save()
            vehicle.parts_used.set(new_parts)
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    
    # Get all parts, not just available ones
    all_parts = Part.objects.all()
    
    # Get the currently selected parts for this vehicle
    selected_parts = list(vehicle.parts_used.all().values_list('id', flat=True))
    
    return render(request, 'inventory/edit_vehicle.html', {
        'form': form,
        'vehicle': vehicle,
        'parts': all_parts,
        'selected_parts': selected_parts  # Pass the selected parts IDs to the template
    })



def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    for part in vehicle.parts_used.all():
        part.quantity += 1
        part.save()
    vehicle.delete()
    messages.success(request, 'Vehicle deleted successfully!')
    return redirect('vehicle_list')



def parts_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        parts = Part.objects.filter(
            name__icontains=search_query) | Part.objects.filter(
            category__icontains=search_query) | Part.objects.filter(
            serial_number__icontains=search_query)
    else:
        parts = Part.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            current_time = timezone.now()
            part.created_at = current_time 
            part.updated_at = current_time
            part.save()
            messages.success(request, 'Part added successfully!')
            return redirect('parts_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PartForm()
    
    return render(request, 'inventory/parts_list.html', {
        'parts': parts,
        'form': form,
        'search_query': search_query
    })

def edit_part(request, pk):
    part = get_object_or_404(Part, pk=pk)
    if request.method == 'POST':
        form = PartForm(request.POST, instance=part)
        if form.is_valid():
            part = form.save(commit=False)
            part.updated_at = datetime.now()
            part.save()
            messages.success(request, 'Part updated successfully!')
            return redirect('parts_list')
    else:
        form = PartForm(instance=part)
    return render(request, 'inventory/edit_part.html', {
        'form': form,
        'part': part
    })


def delete_part(request, pk):
    part = get_object_or_404(Part, pk=pk)
    part.delete()
    return redirect('parts_list')

def bill_list(request):
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    bills = Bill.objects.all().order_by('-created_at')
    
    if search_query:
        bills = bills.filter(
            bill_number__icontains=search_query) | bills.filter(
            customer_name__icontains=search_query) | bills.filter(
            description__icontains=search_query)
    
    if start_date:
        bills = bills.filter(date__gte=start_date)
    if end_date:
        bills = bills.filter(date__lte=end_date)
    
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_at = timezone.now()
            bill.save()
            
            # Save many-to-many relationships after saving the form
            form.save_m2m()
            
            messages.success(request, 'Bill added successfully!')
            return redirect('bill_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BillForm()
    
    # Get all parts for the form
    parts = Part.objects.all()
    
    return render(request, 'inventory/bill_list.html', {
        'bills': bills,
        'form': form,
        'parts': parts,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date
    })

def edit_bill(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bill updated successfully!')
            return redirect('bill_list')
    else:
        form = BillForm(instance=bill)
    
    # Get all parts for the form
    parts = Part.objects.all()
    
    return render(request, 'inventory/edit_bill.html', {
        'form': form,
        'bill': bill,
        'parts': parts
    })

def delete_bill(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    bill.delete()
    return redirect('bill_list')

def export_data(request):
    context = {
        'total_vehicles': Vehicle.objects.count(),
        'total_parts': Part.objects.count(),
        'total_bills': Bill.objects.count(),
    }
    return render(request, 'inventory/export_data.html', context)

def export_vehicles_excel(request):
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    
    vehicles = Vehicle.objects.all()
    
    # Apply date filtering if dates are provided
    if from_date_str and to_date_str:
        # Parse the date strings
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        
        # Convert to datetime objects
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Make them timezone-aware
        from_datetime = timezone.make_aware(from_datetime)
        to_datetime = timezone.make_aware(to_datetime)
        
        # Filter vehicles by created_at date
        vehicles = vehicles.filter(created_at__range=[from_datetime, to_datetime])
    
    headers = ['Owner Name', 'Model', 'Registration Number', 'Description', 'Parts Used', 'Created At']
    fields = ['owner_name', 'model', 'registration_number', 'description', 'parts_used_display', 'created_at']
    
    # Convert queryset to make datetime timezone-naive
    for vehicle in vehicles:
        vehicle.created_at = vehicle.created_at.replace(tzinfo=None)
    
    content = generate_excel(vehicles, headers, fields)
    
    date_range = ""
    if from_date_str and to_date_str:
        date_range = f"_{from_date_str}_to_{to_date_str}"
    
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="vehicles{date_range}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response

def export_parts_excel(request):
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    
    parts = Part.objects.all()
    
    # Apply date filtering if dates are provided
    if from_date_str and to_date_str:
        # Parse the date strings
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        
        # Convert to datetime objects
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Make them timezone-aware
        from_datetime = timezone.make_aware(from_datetime)
        to_datetime = timezone.make_aware(to_datetime)
        
        # Filter parts by created_at date
        parts = parts.filter(created_at__range=[from_datetime, to_datetime])
    
    headers = ['Name', 'Category', 'Serial Number', 'Quantity', 'Price']
    fields = ['name', 'category', 'serial_number', 'quantity', 'price']
    
    # Convert queryset to make datetime timezone-naive
    for part in parts:
        if hasattr(part, 'created_at'):
            part.created_at = part.created_at.replace(tzinfo=None)
    
    content = generate_excel(parts, headers, fields)
    
    date_range = ""
    if from_date_str and to_date_str:
        date_range = f"_{from_date_str}_to_{to_date_str}"
    
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="parts{date_range}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response

def export_bills_excel(request):
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    
    bills = Bill.objects.all()
    
    # Apply date filtering if dates are provided
    if from_date_str and to_date_str:
        # Parse the date strings
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        
        # Convert to datetime objects
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Make them timezone-aware
        from_datetime = timezone.make_aware(from_datetime)
        to_datetime = timezone.make_aware(to_datetime)
        
        # Filter bills by date
        bills = bills.filter(date__range=[from_datetime, to_datetime])
    
    # Create a workbook and add a worksheet
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Bills')
    
    # Define styles
    header_style = xlwt.easyxf('font: bold True; alignment: horizontal center')
    date_style = xlwt.easyxf(num_format_str='DD-MM-YYYY')
    
    # Customize these headers based on your actual Bill model fields
    headers = ['Bill ID', 'Bill Number', 'Customer Name', 'Date', 'Total Amount', 'Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_style)
    
    # Write data rows
    for row, bill in enumerate(bills, 1):
        worksheet.write(row, 0, bill.id)
        worksheet.write(row, 1, bill.bill_number)
        worksheet.write(row, 2, bill.customer_name)
        worksheet.write(row, 3, bill.date, date_style)
        worksheet.write(row, 4, bill.total_amount)
        worksheet.write(row, 5, bill.status)
    
    # Set column widths
    for col in range(len(headers)):
        worksheet.col(col).width = 256 * 20  # 20 characters wide
    
    # Create HTTP response with Excel file
    date_range = ""
    if from_date_str and to_date_str:
        date_range = f"_{from_date_str}_to_{to_date_str}"
    
    response = HttpResponse(content_type='application/ms-excel')
    filename = f'bills{date_range}_{datetime.now().strftime("%Y%m%d")}.xls'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Save the workbook to the response
    workbook.save(response)
    
    return response


def view_bill(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'inventory/view_bill.html', {
        'bill': bill,
        'parts_used': bill.parts_used.all()
    })

def delete_bill(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    bill.delete()
    return redirect('bill_list')


def delete_all_data(request):
    if request.method == 'POST':
        # Delete all data from the database
        Vehicle.objects.all().delete()
        Part.objects.all().delete()
        Bill.objects.all().delete()
        # Add any other models that need to be cleared
        
        messages.success(request, 'All data has been successfully deleted from the system.')
        return redirect('export_data')
    
    return redirect('export_data')

