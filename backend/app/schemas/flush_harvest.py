from marshmallow import Schema, fields, validate


class FlushHarvestCreateSchema(Schema):
    room_id = fields.Int(required=True, data_key="roomId")
    harvested_at = fields.DateTime(required=True, data_key="harvestedAt")
    flush_no = fields.Int(required=True, data_key="flushNo", validate=validate.Range(min=1))
    weight_kg = fields.Float(
        required=True,
        data_key="weightKg",
        validate=validate.Range(min=0.0001, error="weightKg 须大于 0"),
    )
    grade = fields.Str(required=True, validate=validate.OneOf(["A", "B", "C"]))
    operator_name = fields.Str(required=True, data_key="operatorName", validate=validate.Length(min=1, max=64))


class FlushHarvestOutSchema(Schema):
    id = fields.Int(dump_only=True)
    room_id = fields.Int(data_key="roomId")
    harvested_at = fields.DateTime(data_key="harvestedAt")
    flush_no = fields.Int(data_key="flushNo")
    weight_kg = fields.Float(data_key="weightKg")
    grade = fields.Str()
    operator_name = fields.Str(data_key="operatorName")
    tide_key = fields.Method("dump_tide_key", data_key="tideKey")

    def dump_tide_key(self, obj):
        return f"{obj.room_id}:{obj.flush_no}"


def assert_unique_flush_in_room(rows):
    by_flush = {}
    for r in rows:
        by_flush[r.flush_no] = r
    assert len(by_flush) == len(rows), "duplicate flushNo in list"
    return rows
