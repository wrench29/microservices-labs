import asyncio
import json
import random
import string
import os
from typing import IO, Final

import aio_pika
from fastapi import UploadFile

import image_repo

RMQ_CONN: Final = "amqp://guest:guest@rabbitmq/"
RABBIT_REPLY: Final = "amq.rabbitmq.reply-to"


def is_valid_image(filename: str) -> bool:
    valid_extensions = [".png", ".jpg", ".jpeg", ".webp"]
    for ext in valid_extensions:
        if filename.endswith(ext):
            return True
    return False


async def save_uploaded_image(image: UploadFile) -> str:
    new_image_id = _generate_random_id()
    _save_original_image(image.file, new_image_id, image.filename)
    thumbnails = await _save_thumbnails(new_image_id, image.filename)
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
    with open(f"uploads/{image_id}/{original_name}", "wb+") as f:
        f.write(file.read())


async def _save_thumbnails(image_id: str, original_name: str) -> dict:
    connection = await aio_pika.connect_robust(RMQ_CONN)

    async with connection:
        channel = await connection.channel()

        callback_queue = await channel.get_queue(RABBIT_REPLY)

        rq = asyncio.Queue(maxsize=1)

        consumer_tag = await callback_queue.consume(
            callback=rq.put,
            no_ack=True,
        )

        request = {
            "image_id": image_id,
            "original_name": original_name,
        }

        await channel.default_exchange.publish(
            message=aio_pika.Message(
                body=json.dumps(request).encode(),
                reply_to=RABBIT_REPLY
            ),
            routing_key="thumbnail-queue"
        )

        response = await rq.get()
        await callback_queue.cancel(consumer_tag)
        return json.loads(response.body)


def _generate_random_id() -> str:
    return ''.join(random.choice(string.ascii_lowercase +
                                 string.digits +
                                 string.ascii_uppercase) for _ in range(32))
