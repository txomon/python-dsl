# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import copy

from python_dsl.configurations import allow_anything
from python_dsl.configurations.allow_all import allow_anything_schema

simple_script_validation_schema = copy.deepcopy(allow_anything_schema)
simple_script_validation_schema.update({
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
    # Names are important too
    'Name': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {
                    'type': 'string',
                    'regex': r'^(?!_).*$',  # We don't let the underscore starting attributes
                }
            }
        }
    },

})
