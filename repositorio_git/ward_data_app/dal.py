"""
Data Access Layer (DAL) for the hospital database.

This module abstracts all database interaction, providing a consistent
interface for the rest of the application. It is configured via
`settings.HOSPITAL_CONFIG` to support different DBMS and data schemas.
"""
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import connections
from django.http import Http404

from .utils import dictfetchall, dictfetchone, format_hour, safe_strftime
from .logging_config import setup_logger

logger = setup_logger(__name__, log_to_file=True, log_level=logging.DEBUG)

DB_TYPE = settings.DB_TYPE
# Define the correct SQL parameter marker for the configured DBMS.
# This is essential to ensure query portability.
PARAM_STYLE = '?' if DB_TYPE == 'sqlserver' else '%s'


def _get_config_value(key_path, default=None):
    """Securely fetches a nested configuration value from `settings.HOSPITAL_CONFIG`."""
    config = settings.HOSPITAL_CONFIG
    keys = key_path.split('.')
    value = config
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        logger.warning(f"Config key not found: '{key_path}'. Using default: {default}")
        return default
    except Exception as e:
        logger.error(f"Unexpected error fetching config '{key_path}': {e}")
        return default


def _execute_query(sql_key=None, params=None, fetch_one=False, sql=None):
    """
    Single entry point for query execution, ensuring centralized management
    of connections, cursors, and exception handling.
    """
    if sql is None:
        sql = _get_config_value(f"queries.{sql_key}")
    if not sql:
        raise ValueError(f"Query not configured or empty for key: {sql_key}")

    # Replace placeholders if using sqlserver
    if PARAM_STYLE == '?':
        sql = sql.replace('%s', '?')

    try:
        with connections['hospital'].cursor() as cursor:
            cursor.execute(sql, params or [])
            if fetch_one:
                return dictfetchone(cursor) # Returns a single dictionary
            else:
                return dictfetchall(cursor) # Returns a list of dictionaries
    except Exception as e:
        logger.error(f"DAL Error executing query '{sql_key or 'raw SQL'}': {e}", exc_info=True)
        raise


# -----------------------------------------------------------------------------
# Data Standardization Functions (`_standardize_*`)
#
# This block's purpose is to decouple the application logic from the
# database column names. Each function maps a raw DB result
# to a Python dictionary with a stable, well-defined structure.
# -----------------------------------------------------------------------------

def _standardize_internado(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'episode_id': str(raw_dict.get(col_map.get('internado_pk'))),
        'patient_name': raw_dict.get(col_map.get('nome')),
        'sala': str(raw_dict.get(col_map.get('sala_id'), '')),
        'cama': raw_dict.get(col_map.get('cama_id'), ''),
        'data_entrada': safe_strftime(raw_dict.get(col_map.get('data_entrada'))),
        'hora_entrada': format_hour(raw_dict.get(col_map.get('hora_entrada'))),
        'specialty_name': raw_dict.get(col_map.get('specialty_name'))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_fenomeno(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'dta_fenom': safe_strftime(raw_dict.get(col_map.get('data_fenomeno'))),
        'hora_fenom': format_hour(raw_dict.get(col_map.get('hora_fenomeno'))),
        'fenomeno': raw_dict.get(col_map.get('fenomeno')),
        'def_fenom': raw_dict.get(col_map.get('definicao_fenomeno'))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_medicacao(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'farmaco': raw_dict.get(col_map.get('farmaco')),
        'via': raw_dict.get(col_map.get('via')),
        'dose': raw_dict.get(col_map.get('dose')),
        'horario': raw_dict.get(col_map.get('horario_medicacao')),
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_atitude(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'atitude': raw_dict.get(col_map.get('atitude')),
        'hora_at': raw_dict.get(col_map.get('horario_atitude'))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_analise(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'analise': raw_dict.get(col_map.get('analise')),
        'dta_anl': safe_strftime(raw_dict.get(col_map.get('data_analise'))),
        'hora_anl': format_hour(raw_dict.get(col_map.get('hora_analise')))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_exame(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'exame': raw_dict.get(col_map.get('exame')),
        'dta_exm': safe_strftime(raw_dict.get(col_map.get('data_exame')))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_diario(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'diario': raw_dict.get(col_map.get('diario')),
        'hora_dir': format_hour(raw_dict.get(col_map.get('hora_diario'))),
        'dta_dir': safe_strftime(raw_dict.get(col_map.get('data_diario')))
    }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_observacoes(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = { 'observacoes':raw_dict.get(col_map.get('observacoes')) }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_pessoa_signif(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = { 'pessoa_signif':raw_dict.get(col_map.get('pessoa_signif')) }
    return {k: v for k, v in standardized.items() if v is not None}

def _standardize_telefone(raw_dict):
    if not raw_dict: return None
    col_map = _get_config_value('columns', {})
    standardized = {
        'telefone_morada':raw_dict.get(col_map.get('telefone_morada')),
        'telemovel':raw_dict.get(col_map.get('telemovel')),
    }
    return {k: v for k, v in standardized.items() if v is not None}

# -----------------------------------------------------------------------------
# Public DAL Interface
# -----------------------------------------------------------------------------

def get_specialties_list() -> list[dict]:
    """Returns a list of all specialties with interned patients."""
    try:
        return _execute_query('get_specialties')
    except Exception as e:
        logger.error(f"Error fetching specialties list: {e}", exc_info=True)
        return []

def get_all_patient_ids() -> list[Decimal]:
    """Returns a list of all interned patient IDs."""
    pk_col = _get_config_value('columns.internado_pk')
    results = _execute_query('get_all_patient_ids')
    return [row[pk_col] for row in results if pk_col in row]


def get_recent_patients_list(specialty_id: str | None = None) -> list[dict]:
    """Returns a list of recent patients, with an optional specialty filter."""
    sql = _get_config_value('queries.get_recent_patients')
    params = []
    
    if specialty_id:
        sql = sql.replace("ORDER BY", f"WHERE i.servicoID = {PARAM_STYLE} ORDER BY")
        params.append(specialty_id)
    
    raw_results = _execute_query(sql=sql, params=params)
    return [_standardize_internado(row) for row in raw_results if row]


def get_paginated_patient_list(page: int, limit: int, specialty_id: str | None = None, sort_key: str = 'admission_date', sort_dir: str = 'desc', search_query: str = '') -> tuple[list[dict], int]:
    """Returns a paginated list, with optional specialty filter."""
    pk_col_name = _get_config_value('columns.internado_pk')
    name_col_name = _get_config_value('columns.nome')
    
    sql_base = _get_config_value('queries.get_patient_list_base')
    sql_count_base = _get_config_value('queries.get_patient_list_count_base')
    if not sql_base or not sql_count_base:
        raise ValueError("Base pagination queries are not configured.")

    params = []
    where_clauses = []
    
    if specialty_id:
        where_clauses.append(f"i.servicoID = {PARAM_STYLE}")
        params.append(specialty_id)
    
    if search_query:
        # Check if the search query is a numeric ID first
        try:
            search_decimal = Decimal(search_query)
            where_clauses.append(f"i.{pk_col_name} = {PARAM_STYLE}")
            params.append(search_decimal)
        except (ValueError, TypeError, InvalidOperation):
            # If not numeric, search by name
            where_clauses.append(f"UPPER(d.{name_col_name}) LIKE {PARAM_STYLE}")
            params.append(f"%{search_query.upper()}%")
    
    sql_where_part = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Get total count with filters
    total_patients = _execute_query(sql=sql_count_base + sql_where_part, params=params, fetch_one=True).get('TOTAL', 0)
    if total_patients == 0:
        return [], 0

    # Prepare sorting
    sort_map = _get_config_value('sorting.patient_list', {})
    db_sort_col = sort_map.get(sort_key)
    direction = "DESC" if sort_dir == 'desc' else "ASC"
    
    alias = 'd' if sort_key == 'name' else 'i'
    order_sql = f" ORDER BY {alias}.{db_sort_col} {direction}"
    
    # Add secondary sort by time if sorting by admission date
    if sort_key == "admission_date" and 'admission_time' in sort_map:
        order_sql += f", i.{sort_map['admission_time']} {direction}"
    
    sql_data = sql_base + sql_where_part + order_sql
    
    offset = (page - 1) * limit
    
    # Pagination syntax is DBMS-dependent
    if DB_TYPE == 'postgres':
        sql_data += f" LIMIT {PARAM_STYLE} OFFSET {PARAM_STYLE}"
        params_data = params + [limit, offset]
    elif DB_TYPE in ['oracle', 'sqlserver']:
        sql_data += f" OFFSET {PARAM_STYLE} ROWS FETCH NEXT {PARAM_STYLE} ROWS ONLY"
        params_data = params + [offset, limit]
    else:
        raise NotImplementedError(f"Pagination not implemented for: {DB_TYPE}")

    raw_results = _execute_query(sql=sql_data, params=params_data)

    # Post-process: Fetch last diary entry for each patient in the list
    standardized_list = []
    sql_last_diary_key = _get_config_value('queries.get_ultimo_diario_chave')
    sql_last_diary_text = _get_config_value('queries.get_ultimo_diario_texto')

    for row in raw_results:
        patient_data = _standardize_internado(row)
        if not patient_data: continue
        
        # This N+1 query (one per patient) is acceptable for a small page size (e.g., 10)
        if sql_last_diary_key and sql_last_diary_text:
            try:
                row_pk = Decimal(patient_data['episode_id'])
                key_res = _execute_query(sql=sql_last_diary_key, params=[row_pk], fetch_one=True)
                if key_res:
                    date_val, time_val = key_res.get('DATA_DIARIO'), key_res.get('HORA_DIARIO')
                    diary_res = _execute_query(sql=sql_last_diary_text, params=[row_pk, date_val, time_val], fetch_one=True)
                    patient_data['ultimo_diario'] = diary_res.get('ULT_DIARIO') if diary_res else None
            except Exception as e:
                logger.warning(f"DAL: Error fetching last diary for {patient_data['episode_id']}: {e}")
        
        standardized_list.append(patient_data)

    return standardized_list, total_patients


def get_patient_details_all(patient_id_str: str, specialty_id: str | None) -> dict | None:
    """
    Aggregates all information for a single patient, ensuring they belong
    to the selected specialty (if one is provided).
    """
    try:
        pk_decimal = Decimal(patient_id_str)
    except (ValueError, TypeError, InvalidOperation):
        raise Http404("Invalid patient ID.")

    sql = _get_config_value('queries.get_patient_details')
    params = [pk_decimal]

    # If a specialty is selected, enforce it in the query
    if specialty_id:
        sql += f" AND i.servicoID = {PARAM_STYLE}"
        params.append(specialty_id)

    raw_details = _execute_query(sql=sql, params=params, fetch_one=True)
    
    if not raw_details:
        if specialty_id:
            logger.warning(f"Access attempt for patient {patient_id_str} not in specialty {specialty_id}.")
            raise Http404("Patient not found or does not belong to this specialty.")
        else:
            raise Http404("Patient not found.")
        
    context = _standardize_internado(raw_details)
    if not context:
        raise ValueError("Failed to standardize patient details.")
    
    # Fetch related data using the primary key
    history_code = _get_config_value('parameters.ainicial_antecedentes_item')
    diagnosis_code = _get_config_value('parameters.ainicial_diagnostico_item')
    admission_note_items = _execute_query('get_ainicial_items', params=[pk_decimal, history_code, diagnosis_code])
    
    # Use dict.fromkeys to get unique values while preserving order
    context['antecedentes'] = list(dict.fromkeys(i.get('VALOR') for i in admission_note_items if i.get('ITEM') == history_code and i.get('VALOR')))
    context['diagnostico'] = list(dict.fromkeys(i.get('VALOR') for i in admission_note_items if i.get('ITEM') == diagnosis_code and i.get('VALOR')))

    # Fetch all other related information sections
    context['telefone'] = [_standardize_telefone(t) for t in _execute_query('get_telefone', params=[pk_decimal]) if t]
    context['observacoes'] = [_standardize_observacoes(o) for o in _execute_query('get_observacoes', params=[pk_decimal]) if o]
    context['pessoa_signif'] = [_standardize_pessoa_signif(p) for p in _execute_query('get_pessoa_signif', params=[pk_decimal]) if p]
    context['fenomenos'] = [_standardize_fenomeno(f) for f in _execute_query('get_fenomenos', params=[pk_decimal]) if f]
    context['medicacao'] = [_standardize_medicacao(m) for m in _execute_query('get_medicacao', params=[pk_decimal]) if m]
    context['atitudes_terapeuticas'] = [_standardize_atitude(a) for a in _execute_query('get_atitudes', params=[pk_decimal]) if a]
    context['analises'] = [_standardize_analise(a) for a in _execute_query('get_analises', params=[pk_decimal]) if a]
    context['exames'] = [_standardize_exame(e) for e in _execute_query('get_exames', params=[pk_decimal]) if e]
    context['diarios'] = [_standardize_diario(d) for d in _execute_query('get_diarios', params=[pk_decimal]) if d]

    return context

def get_patient_id_by_name(patient_name: str, specialty_id: str | None) -> str | None:
    """
    Finds the episode ID of the most recent patient matching a name,
    scoped to a specific specialty.
    """
    try:
        sql = _get_config_value('queries.get_patient_id_by_name')
        params = [f"%{patient_name.upper()}%"]

        if specialty_id:
            sql = sql.replace("WHERE", f"WHERE i.servicoID = {PARAM_STYLE} AND")
            params.insert(0, specialty_id) 
        
        result = _execute_query(sql=sql, params=params, fetch_one=True)
        
        if result:
            pk_col = _get_config_value('columns.internado_pk')
            patient_id = result.get(pk_col)
            if patient_id:
                return str(patient_id)
        
        return None
    except Exception as e:
        logger.error(f"Error fetching ID by name '{patient_name}': {e}", exc_info=True)
        raise