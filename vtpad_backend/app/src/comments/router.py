from fastapi import APIRouter, Depends, BackgroundTasks

from .rto import GetCommentRto
from ..common.crypto import bearer, user_payload
from .service import CommentBugService
from .dto import *

router = APIRouter(
    prefix="/v1/comment",
    tags=["comment"],
    responses={404: {"message": "Not found"}},
)


@router.get('/{bug_id}', dependencies=[Depends(bearer)], response_model=list[GetCommentRto])
async def get_comments(bug_id: str):
    return await CommentBugService.get_comment(bug_id)


@router.post('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetCommentRto)
async def create_comments(bug_id: str, data: CreateCommentDto, token: str = Depends(bearer), background_tasks: BackgroundTasks = BackgroundTasks()):
    return await CommentBugService.create_comment(bug_id, data, user_payload(token), background_tasks)


@router.put('/{comment_id}', dependencies=[Depends(bearer)], response_model=GetCommentRto)
async def update_comments(comment_id: str, data: UpdateCommentDto, token: str = Depends(bearer)):
    return await CommentBugService.update_comment(comment_id, data, user_payload(token))


@router.delete('/{comment_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_comment(comment_id: str, token: str = Depends(bearer)):
    return await CommentBugService.delete_comment(comment_id, user_payload(token))



