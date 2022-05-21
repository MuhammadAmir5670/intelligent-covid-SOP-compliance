from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View

from manager.models import Student
from manager.forms import StudentForm

from manager.utils import save_to_faces_database

def index_student(request):
    students = Student.objects.all()
    return render(request, 'manager/student/list.html', {'students': students})

def show_student(request, id):
    student = get_object_or_404(Student, pk=id)
    return render(request, 'manager/student/show.html', {'student': student})

def create_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            student = form.save()

            images = request.FILES.getlist('images[]')
            save_to_faces_database(images, student)
            return redirect('students-show', id=student.id)
    else:
        form = StudentForm()
    
    return render(request, 'manager/student/create.html', {'form': form})

def update_student(request, id):
    student = get_object_or_404(Student, pk=id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            student = form.save()
            return redirect('students-show', id=student.id)
    else:
        form = StudentForm()
    
    return render(request, 'manager/student/update.html', {'form': form})
