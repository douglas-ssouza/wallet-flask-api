from db import db


class TagModel(db.Model):
  __tablename__ = "tags"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(40), unique=True, nullable=False)

  incomes = db.relationship("IncomeModel", back_populates="tags", secondary="tags_incomes")
  expenses = db.relationship("ExpenseModel", back_populates="tags", secondary="tags_expenses")
