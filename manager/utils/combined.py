from re import A
import cv2
import os
from datetime import datetime, timedelta

from detection import MaskDetector
from manager.models.student import Student
from recognition import FaceRecognizer
from manager.tasks.notifications import send_message
from django.core.files.base import ContentFile
from django.core.cache import cache

from django.conf import settings
from manager.models import Violation

session = {}

def draw(frame, label, identity, location):
    color = MaskDetector.COLORS[label]
    x1, y1, x2, y2 = location

    
    # Draw a box around the face
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    # Draw a label with a name below the face
    cv2.rectangle(frame, (x1, y2 + 35), (x2, y2), color, cv2.FILLED)

    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, label, (x1 + 5, y1 - 10), font, 1, color, 2)
    cv2.putText(frame, identity, (x1 + 6, y2 + 25), font, 1.0, (255, 255, 255), 1)

    return frame, ContentFile(cv2.imencode('.jpg', frame)[1].tobytes())

def update_session(identity):
    if identity not in session.keys():
        return True

    if session[identity] < datetime.now() - timedelta(minutes=3):
        return True
    
    return False

def save_image(identity, image):
    path = settings.MEDIA_ROOT / 'screen' / identity
    os.mkdir(path) if not os.path.exists(path) else None
    image_path = path / f'image-{len(os.listdir(path))}.jpg'
    print(image_path) 
    cv2.imwrite(str(image_path), image)
    return str(image_path)

def merge(frame, mask_detector, face_detector):
    assert isinstance(face_detector, FaceRecognizer), True
    assert isinstance(mask_detector, MaskDetector), True

    merged = []

    for label, coors in mask_detector(frame):
        identities = face_detector(frame[coors[1]:coors[3], coors[0]: coors[2]], key='roll_no')
        if len(identities):
            identity, _ = identities.pop()
            merged.append((label, str(identity), coors))
        else:
            merged.append((label, 'unknown', coors))

    for label, identity, location in merged:
        if identity == 'unknown':
            frame, _ = draw(frame, label, identity, location)
            break
        
        # Fetch the student information and draw on the image
        student = Student.objects.get(roll_no=identity)
        frame, content = draw(frame, label, student.name, location)

        if label != 'mask' and cache.get(identity) is None:
            violation = Violation.objects.create(student=student, violation_type=label)
            violation.screen_shot.save('output.jpg', content)
            violation.save()

            # store student record redis cache for given number of secondss
            cache.set(identity, student, timeout=60) is None
            send_message.delay(violation.id, label)
            
    return frame