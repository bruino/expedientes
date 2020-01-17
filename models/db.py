# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
def custom(form, fields):
        col_label_size = 4
        label_col_class = "col-sm-%d" % col_label_size
        col_class = "col-sm-%d" % (12 - col_label_size)
        offset_class = "col-sm-offset-%d" % col_label_size
        parent = TABLE(_class='table table-borderless',
                       _style='margin-top: 1.5rem')
        for id, label, controls, help in fields:
            # wrappers
            _help = SPAN(help, _class='help-block')
            # embed _help into _controls
            _controls = DIV(controls, _help, _class="%s" % (col_class))
            if isinstance(controls, INPUT):
                if controls['_type'] == 'submit':
                    controls.add_class('btn btn-primary')
                    _controls = DIV(controls, _class="%s %s" %
                                    (col_class, offset_class))
                if controls['_type'] == 'button':
                    controls.add_class('btn btn-secondary')
                elif controls['_type'] == 'file':
                    controls.add_class('input-file')
                elif controls['_type'] in ('text', 'password'):
                    controls.add_class('form-control')
                elif controls['_type'] == 'checkbox' or controls['_type'] == 'radio':
                    controls.add_class('form-check-input')
                    label.add_class('form-check-label')
                    label.insert(0, controls)
                    _controls = DIV(
                        DIV(label, _help, _class="form-check"), _class="%s" % col_class)
                    label = DIV(_class="sm-hidden %s" % label_col_class)
                elif isinstance(controls, SELECT):
                    controls.add_class('custom-select')

                elif isinstance(controls, TEXTAREA):
                    controls.add_class('form-control')

            elif isinstance(controls, SPAN):
                _controls = P(controls.components,
                              _class="form-control-plaintext %s" % col_class)
            elif isinstance(controls, UL):
                for e in controls.elements("input"):
                    e.add_class('form-control')
            elif isinstance(controls, CAT) and isinstance(controls[0], INPUT):
                    controls[0].add_class('form-control')
            if isinstance(label, LABEL):
                label.add_class(
                    'form-control-label font-weight-bold %s' % label_col_class)

            parent.append(
                DIV(label, _controls, _class='form-group row', _id=id))
        return parent

response.formstyle = custom #'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# New widget date
def date_widget(field, value):
    wrapper = DIV()
    input_date = SQLFORM.widgets.date.widget(field, value)
    javascript = SCRIPT("""
        jQuery.datetimepicker.setLocale('es');
            $(function () {
                $("#%s").datetimepicker({
                    format: 'd/m/Y',
                    inline: false,
                    timepicker:false,
                });
            });
    """ % input_date['_id'], _type='text/javascript')
    wrapper.components.extend([input_date,javascript])
    return wrapper

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------
db.define_table('case_file',
    Field('auth_user_id', db.auth_user),
    Field('created_by', 'string', requires=IS_NOT_EMPTY()),
    Field('case_file_subject', 'string'),
    Field('case_file_new', 'string'),
    )

db.define_table('case_file_history',
    Field('case_file_id', db.case_file),
    Field('case_file_ingress', 'date', label='Ingreso'),
    Field('case_file_egress', 'date', label='Egreso'),
    Field('case_file_to', 'string', label='Elevado a'),
    Field('case_file_status', 'string', label='Estado'),
    Field('case_file_notes', 'text', label='Observaciones'),
)

db.case_file_history.case_file_ingress.widget=date_widget
db.case_file_history.case_file_egress.widget=date_widget

db.define_table('case_file_child',
    Field('case_file_id', db.case_file),
    Field('case_file_child_create', 'date'),
    Field('case_file_notes', 'text'),
)

db.case_file.auth_user_id.default=auth.user_id
db.case_file.auth_user_id.writable=False
db.case_file.auth_user_id.label='Usuario'
db.case_file.created_by.requires=IS_NOT_EMPTY()
db.case_file.created_by.label='Creado por'
db.case_file.case_file_subject.requires=IS_NOT_EMPTY()
db.case_file.case_file_subject.label='Asunto'
db.case_file.case_file_new.requires=IS_NOT_EMPTY()
db.case_file.case_file_new.label='Número Expte'
db.case_file_child.case_file_child_create.writable=False
db.case_file_child.case_file_child_create.default=request.now
db.case_file_child.case_file_child_create.label='Fecha'
db.case_file_child.case_file_notes.requires=IS_NOT_EMPTY()
db.case_file_child.case_file_notes.label='Observaciones'

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)
