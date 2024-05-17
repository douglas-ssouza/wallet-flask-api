from db import db


class ExpenseModel(db.Model):
  __tablename__ = "expenses"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(40), unique=False, nullable=False)
  value = db.Column(db.Float(precision=2), unique=False, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
  
  user = db.relationship("UserModel", back_populates="expenses")
  tags = db.relationship("TagModel", back_populates="expenses", secondary="tags_expenses")


  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'value': self.value,
      'user_id': self.user_id,
      'user': self.user,
    }
