from marshmallow import Schema, fields


class PlainUserSchema(Schema):
  id = fields.Int(dump_only=True)
  username = fields.Str(required=True)
  password = fields.Str(required=True, load_only=True)


class PlainExpenseSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  value = fields.Float(required=True)


class PlainIncomeSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  value = fields.Float(required=True)


class UserSchema(PlainUserSchema):
  expenses = fields.List(fields.Nested(PlainExpenseSchema()), dump_only=True)
  incomes = fields.List(fields.Nested(PlainIncomeSchema()), dump_only=True)


class TagSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str()


class ExpenseSchema(PlainExpenseSchema):
  user_id = fields.Int(required=True, load_only=True)
  user = fields.Nested(PlainUserSchema(), dump_only=True)
  tags = fields.List(fields.Nested(TagSchema()), dump_only=True)


class IncomeSchema(PlainIncomeSchema):
  user_id = fields.Int(required=True, load_only=True)
  user = fields.Nested(PlainUserSchema(), dump_only=True)
  tags = fields.List(fields.Nested(TagSchema()), dump_only=True)


class TagAndIncomeSchema(Schema):
  message = fields.Str()
  income = fields.Nested(IncomeSchema)
  tag = fields.Nested(TagSchema)


class TagAndExpenseSchema(Schema):
  message = fields.Str()
  expense = fields.Nested(ExpenseSchema)
  tag = fields.Nested(TagSchema)


class UserUpdateSchema(Schema):
  username = fields.Str(required=True)


class ExpenseUpdateSchema(Schema):
  name = fields.Str()
  value = fields.Float()
  user_id = fields.Int()


class IncomeUpdateSchema(Schema):
  name = fields.Str()
  value = fields.Float() 
  user_id = fields.Int()


class ValueByOperationSchema(Schema):
  operation = fields.Str(required=True)
  value = fields.Float(required=True)


class TotalValueSchema(Schema):
  total = fields.Float(dump_only=True)
  user = fields.Nested(PlainUserSchema(), dump_only=True)