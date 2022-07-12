from django.apps import AppConfig

from manager.utils import load_faces_database_from_db

class ManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "manager"

    Models = None

    def ready(self) -> None:
        from detection import MaskDetector, SocialDistancing
        from recognition import FaceRecognizer
        from manager.models import Student

        ManagerConfig.mask_detection = MaskDetector()
        ManagerConfig.distance_detection = SocialDistancing()
        ManagerConfig.face_recognition = FaceRecognizer(path=False)
        ManagerConfig.combined = [ManagerConfig.mask_detection, ManagerConfig.face_recognition]

        ManagerConfig.face_recognition.database = load_faces_database_from_db(Student.objects.all(), 'name')

        from manager import signals
        return super().ready()
