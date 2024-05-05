

def password_check(password:str)->str|None:
    if len(password)<8:
        return "Password too short, minimum 8 characters!"
    
    return None
