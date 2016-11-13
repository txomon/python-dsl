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

all_asts = [
    'Add',
    'alias',
    'And',
    'arg',
    'arguments',
    'Assert',
    'Assign',
    'AST',
    'AsyncFor',
    'AsyncFunctionDef',
    'AsyncWith',
    'Attribute',
    'AugAssign',
    'AugLoad',
    'AugStore',
    'Await',
    'BinOp',
    'BitAnd',
    'BitOr',
    'BitXor',
    'boolop',
    'BoolOp',
    'Break',
    'Bytes',
    'Call',
    'ClassDef',
    'cmpop',
    'Compare',
    'comprehension',
    'Continue',
    'Del',
    'Delete',
    'Dict',
    'DictComp',
    'Div',
    'Ellipsis',
    'Eq',
    'excepthandler',
    'ExceptHandler',
    'expr',
    'Expr',
    'expr_context',
    'Expression',
    'ExtSlice',
    'FloorDiv',
    'For',
    'FunctionDef',
    'GeneratorExp',
    'Global',
    'Gt',
    'GtE',
    'If',
    'IfExp',
    'Import',
    'ImportFrom',
    'In',
    'Index',
    'Interactive',
    'Invert',
    'Is',
    'IsNot',
    'keyword',
    'Lambda',
    'List',
    'ListComp',
    'Load',
    'LShift',
    'Lt',
    'LtE',
    'MatMult',
    'mod',
    'Mod',
    'Module',
    'Mult',
    'Name',
    'NameConstant',
    'Nonlocal',
    'Not',
    'NotEq',
    'NotIn',
    'Num',
    'operator',
    'Or',
    'Param',
    'Pass',
    'Pow',
    'Raise',
    'Return',
    'RShift',
    'Set',
    'SetComp',
    'slice',
    'Slice',
    'Starred',
    'stmt',
    'Store',
    'Str',
    'Sub',
    'Subscript',
    'Suite',
    'Try',
    'Tuple',
    'UAdd',
    'unaryop',
    'UnaryOp',
    'USub',
    'While',
    'With',
    'withitem',
    'Yield',
    'YieldFrom',
]

allow_anything_schema = {a: allow_anything for a in all_asts}

default_validation_schema = copy.deepcopy(allow_anything_schema)

default_validation_schema.update({
    # Here the document is stored,
    'code': allow_anything,
    # No import statements allowed
    'Import': {
        'type': 'list',
        'items': []
    },
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
                                    'oneof': [  # Avoid redefinition of allowed functions
                                        {
                                            'type': 'string',
                                            'allowed': [],  # Defined functions
                                        },
                                        {
                                            'type': 'string',
                                            'allowed': [  # Allowed functions
                                                'abs',
                                                'all',
                                                'any',
                                                'ascii',
                                                'bin',
                                                'bool',
                                                'bytearray',
                                                'bytes',
                                                'callable',
                                                'chr',
                                                'classmethod',
                                                # 'compile', # Lets you do nasty things
                                                'complex',
                                                # 'delattr', # Can be used to do __ thingies
                                                'dict',
                                                # 'dir', # No instrospection
                                                'divmod',
                                                'enumerate',
                                                # 'eval', # No random string evaluation
                                                # 'exec', # No execution
                                                'filter',
                                                'float',
                                                'format',
                                                'frozenset',
                                                # 'getattr', # Can be used for __ thingies
                                                # 'globals',  # Not needed
                                                'hasattr',  # Mixed feelings
                                                'hash',
                                                # 'help',  # Not interactive
                                                'hex',
                                                'id',
                                                # '__import__', # Not importing through this
                                                # 'input',  # Not interactive
                                                'int',
                                                'isinstance',
                                                'issubclass',
                                                'iter',
                                                'len',
                                                'list',
                                                # 'locals',  # Not needed
                                                'map',
                                                'max',
                                                # 'memoryview',  # Not needed
                                                'min',
                                                'next',
                                                'object',
                                                'oct',
                                                # 'open', # No access to fs
                                                'ord',
                                                'pow',
                                                # 'print', # No access to stdin/stdout/stderr
                                                'property',
                                                'range',
                                                'repr',
                                                'reversed',
                                                'round',
                                                'set',
                                                # 'setattr', # Dangerous __ thingies
                                                'slice',
                                                'sorted',
                                                'staticmethod',
                                                'str',
                                                'sum',
                                                'super',
                                                'tuple',
                                                'type',
                                                # 'vars', # Not needed, __ thingies
                                                'zip',
                                            ]
                                        },
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    # Attribute access should be really constrained
    'Attribute': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'attr': {
                    'type': 'string',
                    'regex': r'^(?!_).*$',  # We don't let the underscore starting attributes
                }
            }
        }
    },
})

_sandbox_validator = None


def get_sandbox_validator():
    global _sandbox_validator
    if _sandbox_validator:
        return _sandbox_validator
    _sandbox_validator = Validator(allow_unknown=False)
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
        name_schema = validation_schema['Call']['schema']['schema']['func']['schema']['Name']['schema']
        calls = name_schema['id']['oneof'][0]['allowed']
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
