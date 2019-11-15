"""Routes for the Code Generator"""
from flask import Blueprint, render_template, request, flash, redirect, session
from app.models import db, Project, Field
from app.gen.coder import write_code
from app.gen.source_dict import source
from app.utils import camel_case
# from app.printvar import printvar

# Blueprint Config
gen_bp = Blueprint('gen_bp', __name__,
                   template_folder='templates',
                   static_folder='static',
                   url_prefix='/gen')


@gen_bp.route('/<int:project_id>')
def generate_code(project_id):
    config = create_config(project_id)
    project_name = config['project_name']

    for (index, table) in enumerate(config["tables"]):
        model_name = config['tables_camelcase'][index]
        tconfig = config[table]
        gen_mod_inifile(project_name, table)
        gen_mod_css(project_name, table)
        gen_add_fields(project_name, table, tconfig)
        gen_edit_fields(project_name, table, tconfig)
        gen_routes(project_name, model_name, table, tconfig['tschema'])
        gen_wtforms(project_name, model_name, table, tconfig['tschema'])
        gen_view_fields(project_name, table, tconfig)
        gen_list_fields(project_name, table, tconfig)
        gen_delete_record(project_name, table, tconfig)

    gen_source_files(project_name, config["tables"])
    gen_models(config)

    return "Code generation is complete!"


def create_config(project_id):
    project = Project.query.get(project_id)
    schema = create_schema(project)
    tables = [table for table in schema]
    tables_camelcase = [camel_case(table) for table in tables]

    config = {}
    config["project_name"] = project.name
    config["conn"] = project.db_uri
    config["tables"] = tables
    config["tables_camelcase"] = tables_camelcase

    add_fields = edit_fields = view_fields = []

    # tschema = table schema
    for table in tables:
        tschema = schema[table]
        config[table] = {
            "tschema": tschema,
            "add_fields": [field for field in tschema if tschema[field]['add']],
            "edit_fields": [field for field in tschema if tschema[field]['edit']],
            "view_fields": [field for field in tschema if tschema[field]['view']],
            "list_fields": [field for field in tschema if tschema[field]['list']]
        }
    return config


# ----------------models.py Generator--------------#
def gen_models(config):
    src_path = "source/app"
    src_file = "models.txt"
    kwargs = config
    output_obj = {"output_path": f"{config['project_name']}/app",
                  "output_file": "models.py"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


# ----------------routes Generator--------------#
def gen_routes(project_name, model_name, table, table_schema):
    src_path = "source/app/module"
    src_file = "routes.txt"
    kwargs = {}
    kwargs['project_name'] = project_name
    kwargs['model_name'] = model_name
    kwargs['table'] = table
    kwargs['table_schema'] = table_schema
    output_obj = {"output_path": f"{project_name}/app/mod_{table}",
                  "output_file": f"{table}_routes.py"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


def gen_wtforms(project_name, model_name, table, table_schema):
    src_path = "source/app/module"
    src_file = "forms.txt"
    kwargs = {}
    kwargs['model_name'] = model_name
    kwargs['table'] = table
    kwargs['table_schema'] = table_schema
    output_obj = {"output_path": f"{project_name}/app/mod_{table}",
                  "output_file": f"{table}_form.py"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


# ----------------HTML Templates Generator--------------#
def gen_add_fields(project_name, table, tconfig):
    """Generate template for create.html page"""
    src_path = "source/app/module/templates"
    src_file = "create.html"
    kwargs = {}
    kwargs["table"] = table
    kwargs["tschema"] = tconfig["tschema"]
    kwargs["add_fields"] = tconfig["add_fields"]
    output_obj = {"output_path": f"{project_name}/app/mod_{table}/templates",
                  "output_file": f"{table}_create.html"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


def gen_edit_fields(project_name, table, tconfig):
    src_path = "source/app/module/templates"
    src_file = "update.html"
    kwargs = {}
    kwargs["table"] = table
    kwargs["tschema"] = tconfig["tschema"]
    kwargs["edit_fields"] = tconfig["edit_fields"]
    output_obj = {"output_path": f"{project_name}/app/mod_{table}/templates",
                  "output_file": f"{table}_update.html"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


def gen_view_fields(project_name, table, tconfig):
    src_path = "source/app/module/templates"
    src_file = "details.html"
    kwargs = {}
    kwargs["table"] = table
    kwargs["tschema"] = tconfig["tschema"]
    kwargs["view_fields"] = tconfig["view_fields"]
    output_obj = {"output_path": f"{project_name}/app/mod_{table}/templates",
                  "output_file": f"{table}_details.html"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


def gen_list_fields(project_name, table, tconfig):
    src_path = "source/app/module/templates"
    src_file = "list.html"
    kwargs = {}
    kwargs["table"] = table
    kwargs["tschema"] = tconfig["tschema"]
    kwargs["list_fields"] = tconfig["list_fields"]
    output_obj = {"output_path": f"{project_name}/app/mod_{table}/templates",
                  "output_file": f"{table}.html"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


def gen_delete_record(project_name, table, tconfig):
    src_path = "source/app/module/templates"
    src_file = "delete.html"
    kwargs = {}
    kwargs["table"] = table
    kwargs["tschema"] = tconfig["tschema"]
    kwargs["view_fields"] = tconfig["view_fields"]
    output_obj = {"output_path": f"{project_name}/app/mod_{table}/templates",
                  "output_file": f"{table}_delete.html"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None
# ----------------End of HTML Templates Generator--------------#


# ----------------__init__.py Generator for every module--------------#
def gen_mod_inifile(project_name, table):
    src_path = "source/app/module"
    src_file = "__init__.txt"
    kwargs = {}
    output_obj = {"output_path": f"{project_name}/app/mod_{table}",
                  "output_file": "__init__.py"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


# ----------------style.css Generator for every module--------------#
def gen_mod_css(project_name, table):
    src_path = "source/app/module/static/css"
    src_file = "style.css"
    kwargs = {}
    output_obj = {"output_path": f"{project_name}/app/mod_{table}",
                  "output_file": "style.css"}
    write_code(src_path, src_file, kwargs, output_obj)
    return None


# ----------------Generate other files from source templates--------------#
def gen_source_files(project_name, tables):
    """Generate other files from source templates"""
    for k, v in source.items():
        filenames = v.split()
        src_path = k.split('__')[0]
        src_file = filenames[0]
        output_file = filenames[1]
        output_path = src_path.replace("source", project_name)
        output_obj = {
            "output_path": output_path,
            "output_file": output_file
        }
        kwargs = {
            "tables": tables
        }

        write_code(src_path, src_file, kwargs, output_obj)

    return None


# ----------------Config functions--------------#
def create_schema(prj_model):
    """Create schema of each table for a given project.
    prj_model is equal to Project.query.get(id)
    """
    schema = {}
    for table in prj_model.tables:
        schema[table.name] = {}
        for field in table.fields:
            schema[table.name][field.name] = {
                "label": field.label,
                "placeholder": field.placeholder,
                "input_type": field.input_type,
                "required": field.required,
                "list": field.list_page,
                "add": field.add_page,
                "edit": field.edit_page,
                "view": field.view_page,
                "default_val": field.default_val,
                "kwargs": field.kwargs
            }
    return schema
