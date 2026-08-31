import os

from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404

from school_project.views import get_base_context

from .models import Result


def results_list(request):
    """Public page showing all published results."""
    results = Result.objects.all()
    return render(
        request,
        'pages/results.html',
        get_base_context({'results': results})
    )


def download_result_file(request, pk):
    """Force the browser to download a result file as an attachment."""

    result = get_object_or_404(Result, pk=pk)

    if not result.result_file:
        raise Http404('No file uploaded for this result.')

    if not result.result_file.storage.exists(result.result_file.name):
        raise Http404('File not found on the server.')

    return FileResponse(
        result.result_file.open('rb'),
        as_attachment=True,
        filename=os.path.basename(result.result_file.name),
    )
