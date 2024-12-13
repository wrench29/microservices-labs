import asyncio
from functools import partial
import json
from typing import Final

import aio_pika
from PIL import Image


IMAGE_SIZES: Final = [64, 256, 512, 1024]


def save_thumbnails(image_id: str, original_name: str) -> dict:
    image = Image.open(f"uploads/{image_id}/{original_name}")
    thumbnails = {}
    for size in IMAGE_SIZES:
        new_image = image.resize((size, size))
        new_image.save(f"uploads/{image_id}/{size}.png")
        thumbnails[size] = f"/static/{image_id}/{size}.png"
    return thumbnails


async def consumer(
    msg: aio_pika.IncomingMessage,
    channel: aio_pika.RobustChannel,
):
    async with msg.process():
        request = json.loads(msg.body)
        response = save_thumbnails(
            request["image_id"], request["original_name"]
        )

        if msg.reply_to:
            await channel.default_exchange.publish(
                message=aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=msg.correlation_id,
                ),
                routing_key=msg.reply_to,
            )


async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/"
    )

    queue_name = "thumbnail-queue"

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)
        await queue.consume(partial(consumer, channel=channel))

        try:
            await asyncio.Future()
        except Exception:
            pass

asyncio.run(main())
