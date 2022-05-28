from django.apps import AppConfig

from detection import mask_detector


class ManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "manager"

    Models = None

    def ready(self) -> None:
        from detection import MaskDetector, SocialDistancing
        from recognition import FaceRecognizer

        ManagerConfig.Models = {
            'mask-detection': MaskDetector(),
            'distance-detection': SocialDistancing(),
            'face-recognition': FaceRecognizer(),
        }

        from manager import signals
        return super().ready()
