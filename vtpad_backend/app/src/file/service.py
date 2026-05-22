import shutil

from fastapi import UploadFile
from .model import FileModel
from ..users.model import UserModel
import datetime

class FileService:
    @staticmethod
    async def save_file(file: UploadFile, user: dict):
        file_location = f'uploads/{file.filename}'
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        avatar = await FileModel.create(filepath=f"/{file_location}")
        await UserModel.filter(id=user.get('id')).update(avatar=avatar)
        temp = await UserModel.filter(id=user.get('id')).get()
        return avatar

    @staticmethod
    async def save_image(file):


        file_location = f'uploads/{file.filename}'
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file = await FileModel.create(filepath=f"/{file_location}")
        return file

    @staticmethod
    async def get_file(file_id: str):
        return await FileModel.filter(id=file_id).get()
