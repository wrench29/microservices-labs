import random
import string
import os
from typing import IO, Final

from PIL import Image
from fastapi import UploadFile

import image_repo

IMAGE_SIZES: Final = [64, 256, 512, 1024]


def is_valid_image(filename: str) -> bool:
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp"]
    for ext in valid_extensions:
        if filename.endswith(ext):
            return True
    return False


async def save_uploaded_image(image: UploadFile) -> str:
    new_image_id = _generate_random_id()
    _save_original_image(image.file, new_image_id, image.filename)
    thumbnails = _save_thumbnails(new_image_id, image.filename)
    original_image_url = f"/static/{new_image_id}/{image.filename}"
    image_repo.save_image(new_image_id, original_image_url, thumbnails)
    return new_image_id


def get_image_info(image_id: str):
    model = image_repo.get_image_by_id(image_id)
    if not model:
        return None
    result = {
        "original": model.original_name
    }
    return result | model.get_thumbnails()


def get_all_images() -> list[str]:
    image_models = image_repo.get_all_images()
    thumbnails = []
    for model in image_models:
        thumbnails.append(model.get_thumbnails()["64"])
    return thumbnails


def _save_original_image(file: IO[bytes], image_id: str, original_name: str):
    os.makedirs(f"uploads/{image_id}")
    Image.open(file).save(f"uploads/{image_id}/{original_name}")


def _save_thumbnails(image_id: str, original_name: str) -> dict:
    image = Image.open(f"uploads/{image_id}/{original_name}")
    thumbnails = {}
    for size in IMAGE_SIZES:
        new_image = image.resize((size, size))
        new_image.save(f"uploads/{image_id}/{size}.png")
        thumbnails[size] = f"/static/{image_id}/{size}.png"
    return thumbnails


def _generate_random_id() -> str:
    return ''.join(random.choice(string.ascii_lowercase +
                                 string.digits +
                                 string.ascii_uppercase) for _ in range(32))
