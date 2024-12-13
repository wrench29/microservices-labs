from fastapi import FastAPI, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import image_service

app = FastAPI()
app.mount("/static", StaticFiles(directory="uploads"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/image/details/{image_id}/", response_class=HTMLResponse)
async def image_detailed(request: Request, image_id: str):
    return templates.TemplateResponse("details.html", {"request": request, "image_id": image_id})


@app.get("/image/")
async def get_images():
    return image_service.get_all_images()


@app.get("/image/{image_id}/")
async def get_image(image_id: str):
    result = image_service.get_image_info(image_id)
    if not result:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "File with specified ID not found")
    return result


@app.post("/image/")
async def post_image(file: UploadFile):
    if not image_service.is_valid_image(file.filename):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "File should be a valid image")
    return {"image_id": await image_service.save_uploaded_image(file)}
