from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # IMPORTANT: media folder ignored on Render, so do NOT force a default media file here.
    image = models.ImageField(upload_to="profile_pics", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        # Save first so file path exists (if uploaded)
        super().save(*args, **kwargs)

        # If no image uploaded, do nothing (avoid crash on Render)
        if not self.image:
            return

        # If storage doesn't provide local path (some deployments), safely skip resize
        try:
            img_path = self.image.path
        except Exception:
            return

        try:
            img = Image.open(img_path)

            # Resize only if bigger than 300x300
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(img_path)
        except Exception:
            # If Pillow can't open/resize for any reason, don't crash production
            return
