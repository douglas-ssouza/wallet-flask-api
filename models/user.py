from db import db


class UserModel(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(40), unique=True, nullable=False)
  password = db.Column(db.String(40), nullable=False)
  
  expenses = db.relationship(
    "ExpenseModel",
    back_populates="user",
    lazy="dynamic",
    cascade="all, delete"
  )
  incomes = db.relationship(
    "IncomeModel",
    back_populates="user",
    lazy="dynamic",
    cascade="all, delete"
  )


  def serialize(self):
    return {
      'id': self.id,
      'username': self.username,
      'password': self.password
    }
