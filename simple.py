def func():
    var = 'asdf'

    def check_var():
        return var == 4

    def check_global_var():
        return var == 4

    def change_var():
        nonlocal var
        var = 4

    info(var)
    info(check_var())
    info(check_global_var())
    change_var()
    info(var)
    info(check_var())
    info(check_global_var())


func()
