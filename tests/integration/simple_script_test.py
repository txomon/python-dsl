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
    "[chr(53)for(vars()[list(vars())[0]])in[1]]",
    "max(open([list(vars())[5]for(password)in[0]][0]))",
    """__builtins__['ww']=().__class__.__base__
__builtins__['w']=ww.__subclasses__()
__builtins__['y']=w[53].__enter__.__func__
__builtins__['a']=y.__globals__['linecache']
__builtins__['os']=a.checkcache.__globals__['os']
os.system('cat *')
().__class__.__base__.__subclasses__()[53].__enter__.__func__.__globals__['linecache'].checkcache.__globals__['os'].system('sh')
""",
"""
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,"KABOOM",(),(),(),"","",0,""
        ),{}
    )()
)()
""",
    """classes = {}.__class__.__base__.__subclasses__()
b = classes[49]()._module.__builtins__
m = b['__import__']('os')
m.system("test")
"""

])
def simple_script_not_allowed_test(test_script):
    validator = SandboxAstValidator(validation_schema=simple_script_validation_schema)
    with pytest.raises(SandboxException):
        validator.validate(test_script)
