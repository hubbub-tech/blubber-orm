

def _execute_for_all_tables(self, operation, skip_tables=False):
    # extra = {}
    # if not skip_tables:
    #     tables = self.get_tables_for_bind(bind)
    #     extra['tables'] = tables
    # op = getattr(self.Model.metadata, operation)
    # op(bind=self.get_engine(app, bind), **extra)
    pass

def create_all(self, bind='__all__', app=None):
    """Creates all tables.

    .. versionchanged:: 0.12
       Parameters were added
    """
    _execute_for_all_tables(app, bind, 'create_all')

def drop_all(self, bind='__all__', app=None):
    """Drops all tables.

    .. versionchanged:: 0.12
       Parameters were added
    """
    _execute_for_all_tables(app, bind, 'drop_all')
