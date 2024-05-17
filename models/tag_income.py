from db import db


class TagIncomeModel(db.Model):
  __tablename__ = "tags_incomes"

  id = db.Column(db.Integer, primary_key=True)
  tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
  income_id = db.Column(db.Integer, db.ForeignKey("incomes.id"))

