import os
import uuid

from django.utils import timezone
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadTo:
    """upload_to that ignores the user-supplied filename (uuid + safe extension)."""

    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        return f"{self.folder}/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}"

    def __eq__(self, other):
        return isinstance(other, UploadTo) and other.folder == self.folder


species_image = UploadTo("species")
site_image = UploadTo("sites")
tree_update_image = UploadTo("tree_updates")
request_image = UploadTo("requests")
report_media = UploadTo("reports")
campaign_image = UploadTo("campaigns")
article_image = UploadTo("articles")
contribution_qr = UploadTo("contribution")
profile_image = UploadTo("profiles")
