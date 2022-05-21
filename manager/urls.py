from django.urls import path

from manager.views import index
from manager.views import index_student, show_student, create_student, update_student

urlpatterns = [
    path('', index, name='dashboard-index'),

    # Students Path
    path('students', index_student, name='students-index'),
    path('students/new', create_student, name='students-new'),
    path('students/<int:id>', show_student, name='students-show'),
    path('students/<int:id>/edit', update_student, name='students-update'),
]