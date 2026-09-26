from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OctadeskPhoneContact(BaseModel):
    model_config = ConfigDict(strict=True)
    number: str
    countryCode: str | None = None
    type: str | None = None
    main: bool | None = None


class OctadeskCustomField(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str | None = None
    value: Any | None = None


class OctadeskContactResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str
    name: str | None = None
    email: str | None = None
    phoneContacts: list[OctadeskPhoneContact] = Field(default_factory=list)
    customFields: list[OctadeskCustomField] = Field(default_factory=list)
