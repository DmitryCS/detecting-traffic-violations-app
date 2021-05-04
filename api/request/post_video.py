from marshmallow import Schema, fields

from api.base import RequestDto


class RequestCreateVideoDtoSchema(Schema):
    file_id = fields.Int(required=True, allow_none=False)


class RequestCreateVideoDto(RequestDto, RequestCreateVideoDtoSchema):
    __schema__ = RequestCreateVideoDtoSchema