from datetime import date
from datetime import timedelta
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


EmailReportField = Literal[
    'summary',
    'short_name',
    'title',
    'state',
    'created_at',
    'updated_at',
]


class EmailReportPreviewDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    space_id: UUID
    date_start: date
    date_end: date
    create_user: UUID | None = None
    fields: list[EmailReportField] = Field(min_length=1, max_length=6)

    @model_validator(mode='after')
    def validate_range_and_fields(self):
        if self.date_end < self.date_start:
            raise ValueError('date_end must be on or after date_start')
        if self.date_end - self.date_start > timedelta(days=366):
            raise ValueError('date range must not exceed 366 days')
        if len(set(self.fields)) != len(self.fields):
            raise ValueError('fields must not contain duplicates')
        return self


class EmailReportRecipientsDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    space_id: UUID


class EmailReportRecipientConfirmation(BaseModel):
    model_config = ConfigDict(extra='forbid')

    recipient_id: UUID
    email: str = Field(min_length=3, max_length=254)


class EmailReportSendDto(BaseModel):
    model_config = ConfigDict(extra='forbid')

    snapshot_id: UUID
    recipient_ids: list[UUID] = Field(min_length=1, max_length=10)
    confirmed_recipients: list[EmailReportRecipientConfirmation] = Field(min_length=1, max_length=10)
    idempotency_key: UUID

    @model_validator(mode='after')
    def reject_duplicate_recipients(self):
        if len(set(self.recipient_ids)) != len(self.recipient_ids):
            raise ValueError('recipient_ids must not contain duplicates')
        confirmed_ids = [recipient.recipient_id for recipient in self.confirmed_recipients]
        if len(set(confirmed_ids)) != len(confirmed_ids) or set(confirmed_ids) != set(self.recipient_ids):
            raise ValueError('confirmed recipients must match recipient_ids')
        return self
