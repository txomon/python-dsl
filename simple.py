import ast, abc
var = 'asdf'


def print_var():
    return var


def change_local_var():
    var = 4


def change_global_var():
    global var
    var = 4


print_var()
change_local_var()
print_var()
change_global_var()
print_var()
