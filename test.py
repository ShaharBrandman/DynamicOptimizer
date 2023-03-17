def checkType(func: callable) -> None:
    if type(func) is bool:
        print('cunt')

def cunt() -> bool:
    return True

checkType(cunt())