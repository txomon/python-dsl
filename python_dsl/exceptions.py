# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


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
