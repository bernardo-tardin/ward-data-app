"""
Utility module with helper functions for data formatting.

This script contains functions to transform raw data obtained from the
Data Access Layer (DAL) into a format suitable for presentation in
templates or other view layers.
"""
import logging

logger = logging.getLogger(__name__)

def format_contacts(home_phone, mobile_phone):
    """
    Combines home and mobile phone numbers into a single formatted string.

    Avoids duplication if numbers are identical and handles cases where one
    or both numbers may be missing.

    Args:
        home_phone (str | None): The landline phone number.
        mobile_phone (str | None): The mobile phone number.

    Returns:
        str: The formatted contacts string.
    """
    if home_phone and mobile_phone:
        # Return both only if they are different, to avoid redundancy
        if home_phone != mobile_phone:
            return f"{home_phone} / {mobile_phone}"
        else:
            return home_phone
    # Return whichever exists, or an empty string if both are null
    return home_phone or mobile_phone or ""


def format_context(patient_data: dict) -> dict:
    """
    Transforms a patient's data dictionary into a formatted context for the view.

    This function receives a dictionary with structured data and converts it
    into a "flat" dictionary with formatted strings, ready to be rendered
    directly in an HTML template. It handles null values and formats lists
    and complex objects into simple HTML.

    NOTE: The dictionary *keys* (e.g., 'diagnostico', 'fenomenos') are
    intentionally kept in their original language to match the Django templates.

    Args:
        patient_data (dict): The patient's data dictionary, typically
                             from the Data Access Layer (DAL).

    Returns:
        dict: A context dictionary with values ready for presentation.
    """
    if not patient_data:
        logger.warning("format_context was called with empty or null patient_data.")
        return {}
        
    context = {}
    
    # Direct mapping and default value handling
    context['episode_id'] = str(patient_data.get('episode_id'))
    context['patient_name'] = patient_data.get('patient_name', 'Name not found')
    context['specialty_name'] = patient_data.get('specialty_name', 'No Specialty')
    context['sala'] = str(patient_data.get('sala', '-------'))
    context['cama'] = patient_data.get('cama', '-------')
    context['data_entrada'] = patient_data.get('data_entrada')
    context['hora_entrada'] = patient_data.get('hora_entrada')
    context['data_saida'] = patient_data.get('data_saida')
    context['hora_saida'] = patient_data.get('hora_saida')

    # Convert lists to comma-separated strings
    context['antecedentes'] = ' ,'.join(patient_data.get('antecedentes', []))
    context['diagnostico'] = ' ,'.join(patient_data.get('diagnostico', []))

    # Process nested structures like contacts
    contacts = patient_data.get('telefone', [])
    phones = [format_contacts(t.get('telefone_morada'), t.get('telemovel')) for t in contacts]
    context['telefone'] = ', '.join(phones) if phones else '-------'

    context['observacoes'] = ' ,'.join([o.get('observacoes', '') for o in patient_data.get('observacoes', [])])
    context['pessoa_signif'] = ' ,'.join([p.get('pessoa_signif', '') for p in patient_data.get('pessoa_signif', [])])

    # Generate small HTML snippets for complex lists
    context['fenomenos'] = ''.join([
        f"<span><strong>{f.get('fenomeno')}</strong> ({f.get('dta_fenom')} {f.get('hora_fenom')})</span>"
        + (f"<span>{f.get('def_fenom')}</span>" if f.get('def_fenom') else "")
        for f in patient_data.get('fenomenos', [])
    ])
    context['medicacao'] = ''.join([
        f"<span>{m.get('farmaco', '?')} - {m.get('via', '?')} - {m.get('dose', '?')}</span>"
        for m in patient_data.get('medicacao', [])
    ])
    context['atitudes_terapeuticas'] = ''.join([
        f"<span>{a.get('atitude', 'OTHER INTERVENTION')} (Time: {a.get('hora_at')})</span>" if a.get('hora_at')
        else f"<span>{a.get('atitude', 'OTHER INTERVENTION')}</span>"
        for a in patient_data.get('atitudes_terapeuticas', [])
    ])
    context['analises'] = ''.join([
        f"<span>{a.get('analise', 'OTHER ANALYSIS')} (Start: {a.get('dta_anl')} {a.get('hora_anl')})</span>"
        for a in patient_data.get('analises', [])
    ])
    context['exames'] = ''.join([
        f"<span>{e.get('exame', 'OTHER EXAM')} (Scheduled: {e.get('dta_exm')})</span>"
        for e in patient_data.get('exames', [])
    ])
    context['diarios'] = ''.join([
        f"<span><strong>{d.get('dta_dir')} {d.get('hora_dir')}</strong></span>"
        + f"<span style='padding-left: 15px;'>{d.get('diario', '').replace(chr(10), '<br>')}</span>"
        for d in patient_data.get('diarios', [])
    ])
    
    return context