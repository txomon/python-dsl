# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from .validator import SandboxAstValidator


def validate_and_run(code, names=None):
    root = SandboxAstValidator().validate(code)
    eval(compile(root, '<unknown>', 'exec'), names or {})
