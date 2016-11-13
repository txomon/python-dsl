# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

from python_dsl.configurations.simple_script import simple_script_validation_schema
from python_dsl.exceptions import SandboxException
from python_dsl.validator import SandboxAstValidator


@pytest.mark.parametrize('test_script', [
    "classes = {}.__class__.__base__.__subclasses__()",
    "b = classes[49]()._module.__builtins__",
    "import ast",
    "a = __builtins__",
])
def simple_script_not_allowed_test(test_script):
    validator = SandboxAstValidator(validation_schema=simple_script_validation_schema)
    with pytest.raises(SandboxException):
        validator.validate(test_script)
