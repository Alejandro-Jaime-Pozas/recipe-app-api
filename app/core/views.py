"""
Core views for app.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response


# this is the basic django view structure as opposed to the class based views normally used
@api_view(['GET'])
def health_check(request):
    """Returns successful response."""
    return Response({'healthy': True})