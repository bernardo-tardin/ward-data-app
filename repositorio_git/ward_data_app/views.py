"""
Views module for the `ward_data_app` application.

This file defines the application's endpoints, including views that render
HTML pages and APIs that provide JSON data to the frontend.
"""
import logging
from io import BytesIO

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.conf import settings

from . import dal
# Import formatter from the correct utility module
from .format_utils import format_context
from .logging_config import setup_logger

logger = setup_logger(__name__, log_to_file=True, log_level=logging.DEBUG)


# Check WeasyPrint availability at application startup.
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.error('WeasyPrint is not installed. PDF generation functionality is disabled.')

# -----------------------------------------------------------------------------
# HTML Page Rendering Views
# -----------------------------------------------------------------------------

@login_required
def home_page_view(request):
    """Renders the main dashboard page."""
    if 'selected_specialty_name' not in request.session:
        return redirect('select_specialty_page')
    return render(request, 'ward_data_app/home.html')


@login_required
def patient_info_page_view(request):
    """Renders the detailed patient information search page."""
    if 'selected_specialty_name' not in request.session:
        return redirect('select_specialty_page')
    return render(request, 'ward_data_app/info-patients.html')

@login_required
def all_patients_page_view(request):
    """Renders the page with the complete list of patients."""
    if 'selected_specialty_name' not in request.session:
        return redirect('select_specialty_page')
    return render(request, 'ward_data_app/all-patients.html')


# -----------------------------------------------------------------------------
# API Endpoints (JSON)
# -----------------------------------------------------------------------------

@login_required
def select_specialty_view(request):
    """
    Handles the specialty selection or the option to view all patients.
    This choice is stored in the user's session.
    """
    specialties = dal.get_specialties_list()

    if request.method == 'POST':
        if 'view_all' in request.POST:
            if 'selected_specialty_id' in request.session:
                del request.session['selected_specialty_id']
            request.session['selected_specialty_name'] = "All Specialties"
            logger.info(f"User '{request.user.username}' selected to view all specialties.")
            return redirect('dashboard_page')

        specialty_id = request.POST.get('specialty_id')
        if specialty_id:
            specialty_name = "Unknown"
            for specialty in specialties:
                # Keys from config.json
                if str(specialty.get('COD_ESPECIALIDADE')) == str(specialty_id):
                    specialty_name = specialty.get('DES_ESPECIALIDADE')
                    break
            
            request.session['selected_specialty_id'] = specialty_id
            request.session['selected_specialty_name'] = specialty_name
            logger.info(f"User '{request.user.username}' selected specialty: {specialty_name} ({specialty_id})")
            return redirect('dashboard_page')
        
    return render(request, 'ward_data_app/select-specialty.html', {'specialties': specialties})


@login_required
def recent_patients_api(request):
    """API endpoint to return recent patients, respecting the session's specialty filter."""
    try:
        specialty_id = request.session.get('selected_specialty_id')
        data = dal.get_recent_patients_list(specialty_id=specialty_id) 
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error in recent_patients_api (view layer): {e}", exc_info=True)
        return JsonResponse({'error': 'Internal error fetching recent patients'}, status=500)


@login_required
def all_patients_api(request):
    """
    API endpoint for a paginated, sorted, and filtered list of all patients.
    Receives GET parameters for pagination, sorting, and search.
    """
    try:
        specialty_id = request.session.get('selected_specialty_id')
        
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "admission_date") 
        sort_order = request.GET.get("sort_order", "desc")
        search_query = request.GET.get("search", "") 

        patients_list, total_count = dal.get_paginated_patient_list(
            specialty_id=specialty_id,
            page=page, 
            limit=limit, 
            sort_key=sort_by, 
            sort_dir=sort_order, 
            search_query=search_query
        )

        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1

        return JsonResponse({
            "patients": patients_list, 
            "total": total_count,
            "page": page, 
            "limit": limit,
            "total_pages": total_pages
        })
    
    except ValueError as ve:
        logger.warning(f"Value error in all_patients_api (view layer): {ve}")
        return JsonResponse({'error': f'Invalid parameter or config error: {ve}'}, status=400)
    except Exception as e:
        logger.error(f"Error in all_patients_api (view layer): {e}", exc_info=True)
        return JsonResponse({'error': 'Internal error fetching patient list'}, status=500)


@login_required
def patient_info_api(request):
    """
    API endpoint that returns the details for a single patient based on a search
    query (either ID or name).
    """
    try:
        specialty_id = request.session.get('selected_specialty_id')
        
        search_query = request.GET.get("search", "").strip()
        if not search_query:
            return JsonResponse({'error': 'Search term not provided.'}, status=400)

        patient_id = None

        # Check if search query is a numeric ID or a name
        if search_query.isdigit():
            patient_id = search_query
            logger.info(f"Searching patient by ID: {patient_id} (Specialty: {specialty_id or 'All'})")
        else:
            logger.info(f"Searching patient by Name: '{search_query}' (Specialty: {specialty_id or 'All'})")
            patient_id = dal.get_patient_id_by_name(search_query, specialty_id)

        if not patient_id:
            raise Http404("Patient not found for the given search term.")

        patient_data = dal.get_patient_details_all(patient_id, specialty_id=specialty_id)
        
        if not patient_data:
             raise Http404(f"Data not found for patient ID {patient_id}.")
             
        return JsonResponse(patient_data)
    
    except Http404 as e:
        logger.warning(f"Patient not found in API patient_info for search '{search_query}': {e}")
        return JsonResponse({'error': 'Patient not found.'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in patient_info_api for search '{search_query}': {e}", exc_info=True)
        return JsonResponse({'error': 'Internal error fetching patient info'}, status=500)

# -----------------------------------------------------------------------------
# File Generation Views
# -----------------------------------------------------------------------------

@login_required
def generate_pdf_view(request, patient_id_str: str):
    """
    Generates and returns a PDF file with a specific patient's details
    "on-the-fly" at the user's request.
    """
    if not WEASYPRINT_AVAILABLE:
        logger.error("Attempted to generate PDF without WeasyPrint installed.")
        return HttpResponse("Server Error: PDF generation library not available.", status=500)

    logger.info(f"Received request to generate PDF for ID: {patient_id_str}")

    try:
        specialty_id = request.session.get('selected_specialty_id')
        
        # 1. Get raw data from DAL
        context = dal.get_patient_details_all(patient_id_str, specialty_id)
        
        # 2. Format data for the template
        context = format_context(context)
        
        # 3. Render template to HTML string
        html_string = render_to_string('ward_data_app/patient-pdf.html', context)

        # 4. Use WeasyPrint to convert HTML string to PDF bytes
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/')) 
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        # 5. Create an HTTP response with the PDF content
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="patient_{context.get("episode_id", "unknown")}.pdf"' 

        logger.info(f"PDF generated successfully for patient ID {patient_id_str}")
        return response
    
    except Http404:
        logger.warning(f"Patient not found when generating PDF: ID {patient_id_str}")
        return HttpResponse("Error: Patient not found.", status=404)
    
    except ValueError as ve: 
        logger.error(f"Value/config error generating PDF for patient ID {patient_id_str}: {ve}", exc_info=True)
        return HttpResponse(f"Internal config error generating PDF.", status=500)
    
    except Exception as e: 
        logger.error(f"Unexpected error generating PDF for patient ID {patient_id_str}: {e}", exc_info=True)
        return HttpResponse(f"Unexpected internal error generating PDF.", status=500)