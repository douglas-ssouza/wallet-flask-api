from db import db


class TagExpenseModel(db.Model):
  __tablename__ = "tags_expenses"

  id = db.Column(db.Integer, primary_key=True)
  tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
  expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"))

