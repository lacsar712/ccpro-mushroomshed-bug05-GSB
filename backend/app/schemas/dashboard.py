from marshmallow import Schema, fields


class DashboardStatsSchema(Schema):
    shed_total = fields.Int(data_key="shedTotal")
    fruiting_room_count = fields.Int(data_key="fruitingRoomCount")
    climate_last_24h = fields.Int(data_key="climateLast24h")
    harvest_kg_last_7d = fields.Float(data_key="harvestKgLast7d")
