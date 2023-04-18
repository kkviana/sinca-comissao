from django.contrib.auth.decorators import login_required

def login_required_all(func):
    decorated_view = login_required(func)
    return decorated_view