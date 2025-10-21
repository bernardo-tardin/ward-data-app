"""
Database Router Module.

This file defines the rules for directing Django's database operations
to the correct connections ('default' or 'hospital').
"""

class HospitalRouter:
    """
    A router to direct database operations for the `ward_data_app`.

    This router implements the following business rules:
    1. All read operations for models in the `ward_data_app`
       are directed to the 'hospital' database.
    2. All write operations for models in the `ward_data_app` are
       disallowed, treating the 'hospital' database as read-only.
    3. Migrations for the 'hospital' database are disabled to
       prevent accidental changes to a legacy database schema.
    """

    def db_for_read(self, model, **hints):
        """
        Directs reads for `ward_data_app` to the 'hospital' database.
        """
        if model._meta.app_label == 'ward_data_app':
            return 'hospital'
        # No preference for other apps
        return None

    def db_for_write(self, model, **hints):
        """
        Blocks writes for `ward_data_app`.
        """
        if model._meta.app_label == 'ward_data_app':
            # Returning None prevents the write operation for this app.
            # This is a crucial safeguard for an external database.
            return None
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allows relations between the 'default' and 'hospital' databases.
        """
        db_list = ('default', 'hospital')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controls if a migration operation can run on a specific database.
        """
        if app_label == 'ward_data_app':
            # Prevents `migrate` command from modifying the 'hospital' db
            return db != 'hospital'
        return None