from marshmallow import Schema, fields


class UserOutSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    role = fields.Str()
    display_name = fields.Str(data_key="displayName")


class LoginResponseSchema(Schema):
    access_token = fields.Str(data_key="accessToken")
    token_type = fields.Str(data_key="tokenType")
    user = fields.Nested(UserOutSchema)


class JsonLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
