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
    'ImportFrom': {
        'type': 'list',
        'items': []
    },
    'alias': {
        'type': 'list',
        'items': []
    },
    # Python2 compatibility
    'Print': {
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
                                    'forbidden': [  # Avoid redefinition of allowed functions
                                        'compile',  # Lets you do nasty things
                                        'delattr',  # Can be used to do __ thingies
                                        'dir',  # No instrospection
                                        'eval',  # No random string evaluation
                                        'exec',  # No execution
                                        'getattr',  # Can be used for __ thingies
                                        'globals',  # Not needed
                                        'help',  # Not interactive
                                        '__import__',  # Not importing through this
                                        'input',  # Not interactive
                                        'locals',  # Not needed
                                        'memoryview',  # Not needed
                                        'open',  # No access to fs
                                        'print',  # No access to stdin/stdout/stderr
                                        'setattr',  # Dangerous __ thingies
                                        'vars',  # Not needed, __ thingies
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

    def validate(self, node):
        self.convert_node(node)
        pprint.pprint(self.current_document)
        validation_schema = copy.deepcopy(self.validation_schema)
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
