# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import ast
import copy
import logging
import pprint
from collections import defaultdict

from cerberus.validator import Validator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class SandboxException(Exception):
    def __init__(self, *args, **kwargs):
        self.node = kwargs.pop('node', None)
        super(SandboxException, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(SandboxException, self).__str__() + str(self.node)


class NodeNotAllowed(SandboxException):
    pass


class NodeParameterNotAllowed(SandboxException):
    def __init__(self, *args, **kwargs):
        self.parameter = kwargs.pop('parameter', None)
        super(NodeParameterNotAllowed, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(NodeParameterNotAllowed, self).__str__() + \
               ' parameter ' + self.parameter


allow_anything = {
    'allow_unknown': True,
    'schema': {},
}

default_validation_schema = {
    # Here the document is stored,
    'code': allow_anything,
    # Everything is contained in a Module
    'Module': allow_anything,
    # Ex
    'Expr': allow_anything,
    # We control functions to be used here
    'Call': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'allow_unknown': True,
            'schema': {
                'func': {
                    'type': 'dict',
                    'schema': {
                        'Name': {
                            'type': 'dict',
                            'schema': {
                                'id': {
                                    'type': 'string',
                                    'allowed': [
                                        'print'
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'Name': allow_anything,
    # Loading variables is important
    'Load': allow_anything,
    # Strings shouldn't be a problem
    'Str': allow_anything,
    # Assignation is really needed
    'Assign': allow_anything,
    'Store': allow_anything,
    'FunctionDef': allow_anything,
    'Num': allow_anything,
    'Global': allow_anything,
    'arguments': allow_anything,
}

_sandbox_validator = None


def get_sandbox_validator():
    global _sandbox_validator
    if _sandbox_validator:
        return _sandbox_validator
    _sandbox_validator = Validator(allow_unknown=False)
    # _sandbox_validator.schema_registry.extend({
    #     'anything': anything_schema
    # })
    return _sandbox_validator


class SandboxAstValidator(object):
    def __init__(self, validation_schema=default_validation_schema):
        self.current_document = defaultdict(list)
        self.validation_schema = validation_schema

    def convert_node(self, node):
        """Visit a node."""
        node_type = node.__class__.__name__
        method = 'convert_' + node_type
        conversor = getattr(self, method, self.generic_convert_node)
        python_repr = conversor(node)
        self.current_document[node_type].append(python_repr)
        return python_repr

    def generic_convert_node(self, node):
        """Called if no explicit visitor function exists for a node."""
        python_repr = {}
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                python_repr[field] = defaultdict(list)
                for count, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        python_repr[field][item.__class__.__name__].append(self.convert_node(item))
                    else:
                        python_repr[field][item.__class__.__name__].append(item)
            elif isinstance(value, ast.AST):
                python_repr[field] = {value.__class__.__name__: self.convert_node(value)}
            else:
                python_repr[field] = value
        return python_repr

    def allow_defined_function_calls(self, validation_schema):
        calls = validation_schema['Call']['schema']['schema']['func']['schema']['Name']['schema']['id']['allowed']
        for function_def in self.current_document.get('FunctionDef', []):
            calls.append(function_def['name'])

    def validate(self, node):
        self.current_document['code'] = self.convert_node(node)
        pprint.pprint(self.current_document)
        validation_schema = copy.deepcopy(self.validation_schema)
        self.allow_defined_function_calls(validation_schema)
        validator = get_sandbox_validator()
        validator.validate(self.current_document, schema=validation_schema)
        if validator.errors:
            logger.error(validator.errors)


def validate_and_run(code):
    root = ast.parse(code)
    SandboxAstValidator().validate(root)
    print(ast.dump(root))
    eval(compile(root, '<unknown>', 'exec'), {})


with open('simple.py') as fd:
    validate_and_run(fd.read())
