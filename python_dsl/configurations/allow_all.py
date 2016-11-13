# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from python_dsl.configurations import allow_anything

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