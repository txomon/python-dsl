# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import ast
import logging
import pprint
from collections import defaultdict

from cerberus.validator import Validator

from python_dsl.configurations.simple_script import simple_script_validation_schema
from python_dsl.exceptions import SandboxException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

_sandbox_validator = None


def get_sandbox_validator():
    global _sandbox_validator
    if _sandbox_validator:
        return _sandbox_validator
    _sandbox_validator = Validator(allow_unknown=False)
    return _sandbox_validator


class SandboxAstValidator(object):
    def __init__(self, validation_schema=simple_script_validation_schema):
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
        if hasattr(node, 'lineno'):
            python_repr['lineno'] = node.lineno
        if hasattr(node, 'col_offset'):
            python_repr['col_offset'] = node.col_offset
        return python_repr

    def validate(self, code):
        node = ast.parse(code)
        self.convert_node(node)
        logger.debug(pprint.pformat(self.current_document))
        logger.debug(ast.dump(node))
        validator = get_sandbox_validator()
        validator.validate(self.current_document, schema=self.validation_schema)
        if validator.errors:
            logger.error(validator.errors)
            raise SandboxException(node=node)
        return node
