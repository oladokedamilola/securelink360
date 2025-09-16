from django import template

register = template.Library()

@register.filter
def first_with_user(join_requests, user):
    """Return the first join request for the given user"""
    for request in join_requests:
        if request.user == user:
            return request
    return None