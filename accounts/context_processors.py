# accounts/context_processors.py
from .forms import ProfileEditForm

def profile_edit_form(request):
    if request.user.is_authenticated:
        return {"profile_edit_form": ProfileEditForm(instance=request.user)}
    return {}
