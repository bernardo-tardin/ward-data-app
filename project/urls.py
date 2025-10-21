from django.contrib import admin
from django.urls import path, include
from ward_data_app import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.select_specialty_view, name='select_specialty_page'), 
    path('dashboard/', views.home_page_view, name='dashboard_page'),
    path('info-patient/', views.patient_info_page_view, name='patient_info_page'),
    path('all-patients/', views.all_patients_page_view, name='all_patients_page'),
    
    # API Endpoints
    path('api/recent_patients_api/', views.recent_patients_api, name='recent_patients_api'),
    path('api/patient_info/', views.patient_info_api, name='patient_info_api'),
    path('api/all_patients/', views.all_patients_api, name='all_patients_api'),
    
    # PDF Generation
    path('generate_pdf/<str:patient_id_str>/', views.generate_pdf_view, name='generate_patient_pdf'),
    
    # Auth
    path('accounts/', include('django.contrib.auth.urls')), 
]