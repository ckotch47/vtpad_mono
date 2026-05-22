from fastapi import HTTPException

from .dto import *
from ..spacesuser.model import SpacesUserModel, SpacesUserRole
from ..users.service import UserService
from .model import NotesModel


class NoteService:
    @staticmethod
    async def create_note(space_id: str, note: CreateNoteDto, user_payload: dict):
        user = await UserService.get_user_by_id(user_payload)
        note = await NotesModel.create(
            title=note.title,
            text=note.text,
            createUser_id=user.get('id'),
            spaces_id=space_id
        )
        return note

    @staticmethod
    async def get_notes(space_id: str):
        return await NotesModel.filter(spaces_id=space_id)

    @staticmethod
    async def update_note(note_id: str, note: UpdateNoteDto):
        if note.title:
            await NotesModel.filter(id=note_id).update(title=note.title)
        if note.text:
            await NotesModel.filter(id=note_id).update(text=note.text)
        return await NotesModel.filter(id=note_id).get()

    @staticmethod
    async def delete_note(note_id: str):
        return await NotesModel.filter(id=note_id).delete()

    @staticmethod
    async def check_right_for_edit_note(user_payload: dict, note_id: str):
        note: dict = (await NotesModel.filter(id=note_id).get()).__dict__
        user_right = await SpacesUserModel.filter(spaceId=note.get('spaces_id'), userId=user_payload.get('id')).first()
        if str(note.get('createUser_id')) == str(user_payload.get('id')):
            return True
        if user_right.role == SpacesUserRole.owner:
            return True
        if 'editNotes' in user_right.right and user_right.right['editNotes']:
            return True
        raise HTTPException(status_code=403, detail="not have right")
