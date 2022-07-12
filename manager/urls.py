from django.urls import path

from manager.views import index
from manager.views import index_student, show_student, create_student, update_student, delete_student
from manager.views import stream
from manager.views import encoding

urlpatterns = [
    path('', index, name='dashboard-index'),

    # Students Paths
    path('students', index_student, name='students-index'),
    path('students/new', create_student, name='students-new'),
    path('students/<int:id>', show_student, name='students-show'),
    path('students/<int:id>/edit', update_student, name='students-update'),
    path('students/<int:id>/delete', delete_student, name='students-delete'),

    # Student Encoding Paths
    path('encoding/<int:id>/delete', encoding.delete, name='delete-encoding'),
    path('encoding/<int:id>/activate', encoding.activate, name='activate-encoding'),
    path('encoding/<int:id>/deactivate', encoding.deactivate, name='deactivate-encoding'),

    # Web Camera Paths
    path('stream/', stream.index, name='stream-index'),
    path('stream/validate-source', stream.validate_source, name='stream-validate-source'),
    path('stream/web-cam', stream.web_cam, name='web-cam'),
    path('stream/web-cam/combined', stream.combined, {'model': 'combined'}, name='web-cam-with-model'),
    path('stream/web-cam/<str:model>', stream.web_cam, name='web-cam-with-model'),
    
    path('stream/ip-cam', stream.web_cam, name='ip-cam-with-model'),
    path('stream/ip-cam/<str:model>', stream.web_cam, name='ip-cam-with-model'),
]