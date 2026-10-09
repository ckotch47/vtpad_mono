from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request

from .rto import GetCommentRto
from ..common.crypto import bearer, user_payload
from .service import CommentBugService
from .dto import *
from ..bug.model import BugsModel
from ..common.right_guard import check_user_into_space
from .model import CommentModel

router = APIRouter(
    prefix="/v1/comment",
    tags=["comment"],
    responses={404: {"message": "Not found"}},
)


async def _require_comment_write(comment_id: str | None, bug_id: str | None, request: Request):
    if comment_id:
        comment = await CommentModel.get_or_none(id=comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="not found")
        bug_id = str(comment.bug_id)
    bug = await BugsModel.get_or_none(id=bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="not found")
    await check_user_into_space(str(bug.spaces_id), request, capability="bug_comments")


@router.get('/{bug_id}', dependencies=[Depends(bearer)], response_model=list[GetCommentRto])
async def get_comments(bug_id: str):
    return await CommentBugService.get_comment(bug_id)


@router.post('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetCommentRto)
async def create_comments(bug_id: str, data: CreateCommentDto, request: Request, token: str = Depends(bearer), background_tasks: BackgroundTasks = BackgroundTasks()):
    await _require_comment_write(None, bug_id, request)
    return await CommentBugService.create_comment(bug_id, data, user_payload(token), background_tasks)


@router.put('/{comment_id}', dependencies=[Depends(bearer)], response_model=GetCommentRto)
async def update_comments(comment_id: str, data: UpdateCommentDto, request: Request, token: str = Depends(bearer)):
    await _require_comment_write(comment_id, None, request)
    return await CommentBugService.update_comment(comment_id, data, user_payload(token))


@router.delete('/{comment_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_comment(comment_id: str, request: Request, token: str = Depends(bearer)):
    await _require_comment_write(comment_id, None, request)
    return await CommentBugService.delete_comment(comment_id, user_payload(token))

