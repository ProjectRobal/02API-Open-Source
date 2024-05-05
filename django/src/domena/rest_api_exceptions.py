from rest_framework.exceptions import APIException

class UserExits(APIException):
    status_code = 405
    default_detail = 'Registration failed user with specific username exits!'
    default_code = 'user_exits'