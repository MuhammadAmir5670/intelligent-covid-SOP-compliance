from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods

from django.contrib import messages

from manager.models import Student
from manager.forms import StudentForm
from manager.utils import save_temp_image
from manager.tasks.student import add_faces_to_database


@require_http_methods(['GET'])
def index_student(request):
    students = Student.objects.all()
    return render(request, 'manager/student/list.html', {'students': students})


@require_http_methods(['GET'])
def show_student(request, id):
    student = get_object_or_404(Student.objects.prefetch_related('encodings'), pk=id)
    return render(request, 'manager/student/show.html', {'student': student})


@require_http_methods(['GET', 'POST'])
def create_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            student = form.save()
            images = request.FILES.getlist('images[]')
            add_faces_to_database.delay(save_temp_image(images), student.pk)

            messages.success(request, 'A student has been registered successfully')
            return redirect('students-show', id=student.id)
    else:
        form = StudentForm()
    
    return render(request, 'manager/student/create.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def update_student(request, id):
    student = get_object_or_404(Student, pk=id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            student = form.save()
            images = request.FILES.getlist('images[]')
            add_faces_to_database.delay(save_temp_image(images), student.pk)

            messages.success(request, 'successfully updated student details')
            return redirect('students-show', id=student.id)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'manager/student/update.html', {'form': form})

@require_http_methods(['POST'])
def delete_student(request, id):
    get_object_or_404(Student, pk=id).delete()
    messages.success(request, 'Successfully deleted the Student record')
    return redirect('students-index')