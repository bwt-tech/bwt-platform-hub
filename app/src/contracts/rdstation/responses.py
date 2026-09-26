from pydantic import BaseModel, ConfigDict


class DealStagePayload(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    nickname: str | None = None


class RDStationDealPipeline(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    name: str
    deal_stages: list[DealStagePayload]


class NestedEmailPayload(BaseModel):
    model_config = ConfigDict(strict=True)
    email: str


class NestedPhonePayload(BaseModel):
    model_config = ConfigDict(strict=True)
    phone: str


class NestedContactPayload(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str | None = None
    emails: list[NestedEmailPayload] = []
    phones: list[NestedPhonePayload] = []


class RDStationDeal(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    name: str | None = None
    contacts: list[NestedContactPayload] = []


class RDStationDealWrapper(BaseModel):
    model_config = ConfigDict(strict=True)
    deals: list[RDStationDeal]
