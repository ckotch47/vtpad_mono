from fastapi import APIRouter, Depends
from .dto import  *
from app.src.common.crypto import bearer, user_payload
from .service import NoteService
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix="/v1/notes",
    tags=["notes"],
    responses={404: {"message": "Not found"}},
    deprecated=True
)


@router.get('/{space_id}', dependencies=[Depends(bearer),  Depends(check_user_into_space)])
async def get_notes(space_id: str, token: str = Depends(bearer)):
    return await NoteService.get_notes(space_id)


@router.post('/{space_id}', dependencies=[Depends(bearer),  Depends(check_user_into_space)])
async def create_note(space_id: str, note: CreateNoteDto, token: str = Depends(bearer)):
    return await NoteService.create_note(space_id, note, user_payload(token))


@router.patch('/{note_id}')
async def update_note(note_id: str, note: UpdateNoteDto, token: str = Depends(bearer)):
    await NoteService.check_right_for_edit_note(user_payload(token), note_id)
    return await NoteService.update_note(note_id, note)


@router.delete('/{note_id}')
async def delete_note(note_id: str, token: str = Depends(bearer)):
    await NoteService.check_right_for_edit_note(user_payload(token), note_id)
    return await NoteService.delete_note(note_id)
