from django.shortcuts import render
from .models import Result


def results_list(request):
    """Public page showing all published results."""
    results = Result.objects.all()
    return render(request, 'pages/results.html', {'results': results})
