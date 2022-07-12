from celery.decorators import task
from celery.utils.log import get_task_logger

from manager.models import Student
from manager.utils.firebase import app

logger = get_task_logger(__name__)

@task(name='send_notification_to_user')
def send_message(path, label, voilation):
    student = Student.objects.get(roll_no=label)
    app.add_screenshot(path, student.email, voilation)
    