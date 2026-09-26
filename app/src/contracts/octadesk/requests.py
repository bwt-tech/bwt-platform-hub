from pydantic import BaseModel, ConfigDict


class PhoneContactPayload(BaseModel):
    model_config = ConfigDict(strict=True)
    number: str
    countryCode: str


class OctadeskContactCreateRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str
    email: str
    phoneContacts: list[PhoneContactPayload]


class ChannelObject(BaseModel):
    model_config = ConfigDict(strict=True)
    channel: str
    code: str


class OriginObject(BaseModel):
    model_config = ConfigDict(strict=True)
    contact: ChannelObject


class TargetObject(BaseModel):
    model_config = ConfigDict(strict=True)
    contact: ChannelObject


class TemplateMessageObject(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str


class TemplateMessageContent(BaseModel):
    model_config = ConfigDict(strict=True)
    templateMessage: TemplateMessageObject


class OctadeskChatStartRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    origin: OriginObject
    target: TargetObject
    content: TemplateMessageContent
