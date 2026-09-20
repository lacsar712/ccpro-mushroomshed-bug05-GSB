from marshmallow import Schema, fields, validate


ROOM_STATUSES = ("fruiting", "idle", "sanitize")


class RoomCreateSchema(Schema):
    shed_id = fields.Int(required=True, data_key="shedId")
    room_code = fields.Str(required=True, data_key="roomCode", validate=validate.Length(min=1, max=32))
    species = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    capacity_bags = fields.Int(required=True, data_key="capacityBags", validate=validate.Range(min=1))
    status = fields.Str(required=True, validate=validate.OneOf(ROOM_STATUSES))


class RoomOutSchema(Schema):
    id = fields.Int(dump_only=True)
    shed_id = fields.Int(data_key="shedId")
    room_code = fields.Str(data_key="roomCode")
    species = fields.Str()
    capacity_bags = fields.Int(data_key="capacityBags")
    status = fields.Str()
