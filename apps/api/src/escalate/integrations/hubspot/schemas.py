from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HubSpotTicket(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    properties: dict[str, str | None]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    archived: bool = False


class HubSpotNextPage(BaseModel):
    after: str


class HubSpotPaging(BaseModel):
    next: HubSpotNextPage | None = None


class HubSpotTicketPage(BaseModel):
    results: list[HubSpotTicket]
    paging: HubSpotPaging | None = None

    @property
    def next_cursor(self) -> str | None:
        return self.paging.next.after if self.paging and self.paging.next else None


class HubSpotSyncResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    imported: int
    skipped: int
    pages: int
    next_cursor: str | None = Field(alias="nextCursor")
