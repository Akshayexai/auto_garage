from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/edit/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/<int:pk>/delete/', views.delete_vehicle, name='delete_vehicle'),
    
    path('parts/', views.parts_list, name='parts_list'),
    path('parts/<int:pk>/edit/', views.edit_part, name='edit_part'),
    path('parts/<int:pk>/delete/', views.delete_part, name='delete_part'),
    
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/<int:pk>/edit/', views.edit_bill, name='edit_bill'),
    path('bills/<int:pk>/delete/', views.delete_bill, name='delete_bill'),
    path('bills/<int:pk>/view/', views.view_bill, name='view_bill'),
    path('bills/delete/<int:pk>/', views.delete_bill, name='delete_bill'),
    
    path('export/', views.export_data, name='export_data'),
    path('export/vehicles/excel/', views.export_vehicles_excel, name='export_vehicles_excel'),
    path('export/parts/excel/', views.export_parts_excel, name='export_parts_excel'),
    path('export/bills/excel/', views.export_bills_excel, name='export_bills_excel'),
    path('delete-all-data/', views.delete_all_data, name='delete_all_data'),
]
