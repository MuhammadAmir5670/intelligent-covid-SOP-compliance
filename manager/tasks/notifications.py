from celery.decorators import task
from celery.utils.log import get_task_logger

from manager.models import Violation
from manager.utils.firebase import app
from manager.utils import violation_verbose_values

logger = get_task_logger(__name__)

@task(name='send_notification_to_user')
def send_message(violation_id, label):
    violation = Violation.objects.get(pk=violation_id)
    app.add_screenshot(violation.screen_shot.path, violation.student.email, label)