from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect

def login_required_and_not_staff(function):
    def wrap(request, *args, **kwargs):

        if request.user.is_authenticated():
            if request.user.is_staff:
                messages.add_message(request, messages.INFO, "You dont have access to this page. Please Login again")
                return redirect("/login")                
            else:
                return function(request, *args, **kwargs)
        else:            
            return redirect("/login")
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap