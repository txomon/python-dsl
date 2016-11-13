print('a')
var = 'asdf'


def print_var():
    print(var)


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
