import os
import re
import firebase_admin

from pathlib import Path
from firebase_admin import credentials, messaging, auth
from firebase_admin import storage, firestore
from datetime import datetime
from manager.utils import violation_verbose_values


BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

class FireBaseAdmin:
    def __init__(self, path="firebase-credentials.json") -> None:
        config = credentials.Certificate(BASE_PATH / path)
        firebase_admin.initialize_app(config, {"storageBucket": "covid-sop-compliance.appspot.com"})
        self.bucket = storage.bucket()
        self.db = firestore.client()

    def get_uid_by_email(self, email):
        user = auth.get_user_by_email(email)
        return user.uid

    def send_notification(self, title, message, tokens, payload=None):
        # See documentation on defining a message payload.
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=message, image='https://cdn-icons-png.flaticon.com/512/3365/3365473.png'),
            data=payload,
            tokens=tokens,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send_multicast(message)
        # Response is a message ID string.
        print("Successfully sent message:", response)

    def upload_file(self, path, label):
        file_name, file_extension = os.path.splitext(os.path.basename(path))
        remote_name = f"{datetime.now()}-{file_name}{file_extension}"
        
        blob = self.bucket.blob(f"{label}/{remote_name}")
        blob.upload_from_filename(path)
        blob.make_public()
        return blob.public_url

    def add_screenshot(self, path, email, label):
        uid = self.get_uid_by_email(email)
        user = self.db.collection('users').document(uid).get()
        
        # only create screenshot object if the user is registered
        if user:
            url = self.upload_file(path, label)
            screenshot = self.db.collection('screenshots')

            # Create screenshot object on remote
            screenshot.document().create({
                'uid': user.id,
                'timestamp': datetime.now(),
                'url': url,
                'voilation': label
            })

            self.send_notification(label, f"{user.get('nickname')} has been spotted with {violation_verbose_values[label]}", user.get('tokens'), {
                'name': str(user.get('nickname')),
                'email': str(email),
                'url': str(url),
                'voilation': str(label),
                'timestamp': str(datetime.now()),
            })


app = FireBaseAdmin()

if __name__ == "__main__":
    app.add_screenshot('/home/dev/Documents/Python/face_app/media/faces_database/Abdul Mateen-7056/Abdul_Mateen-7056-2.jpeg', 'mrumair040@gmail.com', 'No Mask')