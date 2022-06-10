import fastapi
import fastapi.security as security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlalchemy.orm as orm
import services
import schemas
from typing import List

app = fastapi.FastAPI()

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users")
async def create_user(
    user: schemas.UserCreate,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    db_user = await services.get_user_by_username(db, user.username)
    if db_user:
        raise fastapi.HTTPException(
            status_code=400, detail="User already exist")

    user = await services.create_user(db, user)

    return await services.create_token(user)


@app.post("/token")
async def generate_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    user = await services.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")
    return await services.create_token(user)


@app.get("/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user


@app.post("/posts", response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.create_post(db=db, post=post, user=user)


@app.get("/posts", response_model=List[schemas.Post])
async def get_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts(db=db)


@app.get("/posts/top", response_model=List[schemas.Post])
async def get_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_top_posts(db=db)


@app.get("/posts/my", response_model=List[schemas.Post])
async def get_my_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_my_posts(db=db, user=user)


@app.post("/posts/adv", response_model=List[schemas.Post])
async def get_user_posts(
    adv_msg: schemas.AdvisoryMessage,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts(db=db, adv_msg=adv_msg)


@app.get("/posts/{post_id}", status_code=200)
async def get_post(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_post(db, post_id, user)


@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    await services.delete_post(db, post_id, user)

    return {"message": "Sucessfully deleted"}


@app.get("/posts/{post_id}/like")
async def post_like(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.post_like(db=db, post_id=post_id, user=user)


@app.get("/posts/{post_id}/cringe")
async def post_like(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.post_cringe(db=db, post_id=post_id, user=user)


@app.get("/images/{image_id}/like")
async def post_like(
    image_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.image_like(db=db, image_id=image_id, user=user)


@app.get("/images/{image_id}/cringe")
async def post_like(
    image_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.image_cringe(db=db, image_id=image_id, user=user)


@app.get("/posts/{post_id}/report", response_model=schemas.Report)
async def report_post(
    post_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.report_post(db, post_id)


@app.get("/reports", response_model=List[schemas.Report])
async def get_reports(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_reports(db, user)


@app.post("/images", response_model=schemas.Image)
async def upload_image(
    file: fastapi.UploadFile,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.upload_image(
        db=db,
        input_file=file,
        user=user
    )


@app.get("/images/top", response_model=List[schemas.Image])
async def get_posts(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_top_images(db=db)


@app.get("/images")
async def get_images(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_images(db=db)


@app.get("/images/{image_name}")
async def get_image(
    image_name: str,
    db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_image(db=db, name=image_name)


@app.get("/")
async def root():
    return {"Messages": "Politota"}
