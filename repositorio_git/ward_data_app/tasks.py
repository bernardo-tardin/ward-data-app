"""
Module for asynchronous tasks (Celery) related to PDF generation.

This script contains the logic for:
1. Defining asynchronous tasks to generate PDF files from an HTML template.
2. Saving the results to the filesystem.
"""
import os
import logging
from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string

from . import dal
from .logging_config import setup_logger
from .utils import slugify
# Import the formatting logic from its single source of truth
from .format_utils import format_context

logger = setup_logger(__name__, log_to_file=True, log_level=logging.DEBUG)

# WeasyPrint import is optional, allowing the app to run
# even if the PDF generation library is not installed.
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint library not found. PDF generation is disabled.")

# -----------------------------------------------------------------------------
# Asynchronous Tasks (Celery)
# -----------------------------------------------------------------------------

@shared_task(bind=True, max_retries=3)
def generate_patient_pdf(self, patient_id):
    """
    Celery task that generates and saves a PDF for a single patient.
    The task can be retried in case of failure.
    """
    if not WEASYPRINT_AVAILABLE:
        logger.error("PDF generation was invoked, but WeasyPrint is not available.")
        return

    try:
        # 1. Fetch raw data from DAL
        context_from_dal = dal.get_patient_details_all(patient_id, specialty_id=None)
        if not context_from_dal:
            logger.warning(f"No context found for patient {patient_id}")
            return

        # 2. Format data using the imported utility
        final_context_for_template = format_context(context_from_dal)
        
        # 3. Render HTML string
        html_string = render_to_string('ward_data_app/patient-pdf.html', final_context_for_template)
        
        # base_url is crucial for WeasyPrint to find static files (CSS, images)
        base_url = getattr(settings, 'SITE_BASE_URL_FOR_PDFS', '/')
        pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

        # 4. Prepare file path and name
        specialty_name = final_context_for_template.get('specialty_name')
        room = final_context_for_template.get('sala')
        bed = final_context_for_template.get('cama')
        episode_id = final_context_for_template.get('episode_id')
        patient_name = final_context_for_template.get('patient_name', 'NAME_NOT_FOUND')
        safe_filename = slugify(patient_name)
        
        # Build the destination path for the offline backup
        specialty_dir_name = slugify(specialty_name) if specialty_name else "No_Specialty"
        room_dir_name = slugify(room) if room else "No_Room"

        target_dir = os.path.join(
            settings.OFFLINE_BACKUP_DIR, 
            specialty_dir_name, 
            room_dir_name
        )

        os.makedirs(target_dir, exist_ok=True)

        file_name = f"{bed}_{episode_id}_{safe_filename}.pdf"
        file_path = os.path.join(target_dir, file_name)

        # 5. Write file
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)

        logger.info(f"PDF for patient {patient_id} saved to {file_path}")
    except Exception as e:
        logger.error(f"Error generating PDF for patient {patient_id}: {e}", exc_info=True)
        # Retry the task after 60 seconds
        raise self.retry(exc=e, countdown=60)


@shared_task
def generate_periodic_pdf_backup():
    """
    Periodic task that finds all active patients and schedules
    a PDF generation task for each one.
    """
    if not WEASYPRINT_AVAILABLE:
        return # Do nothing if the library isn't available
        
    try:
        active_patient_ids = dal.get_all_patient_ids()
    except Exception as e:
        logger.error(f"Error getting active patient IDs for backup: {e}", exc_info=True)
        return

    logger.info(f"Scheduling PDF generation for {len(active_patient_ids)} active patients.")
    for patient_id in active_patient_ids:
        # Send each generation as a separate task to the Celery worker
        generate_patient_pdf.delay(str(patient_id))