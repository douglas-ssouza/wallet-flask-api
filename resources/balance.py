from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from functools import reduce
from models import ExpenseModel, IncomeModel

blp = Blueprint("balance", __name__, description="Operations on balance")


@blp.route("/balance")
class Balance(MethodView):
  @jwt_required()
  @blp.response(200)
  def get(self):
    expenses_response = ExpenseModel.query.all()
    incomes_response = IncomeModel.query.all()
    expenses = [expense.serialize() for expense in expenses_response]
    incomes = [income.serialize() for income in incomes_response]
    total_expenses = reduce(lambda a, b: a + b, [expense["value"] for expense in expenses] , 0)
    total_income = reduce(lambda a, b: a + b, [income["value"] for income in incomes], 0)
    return { "balance": total_income - total_expenses }


@blp.route("/balance/user/<string:user_id>")
class BalanceUser(MethodView):
  @jwt_required()
  @blp.response(200)
  def get(self, user_id):
    expenses_response = ExpenseModel.query.filter(ExpenseModel.user_id==user_id).all()
    incomes_response = IncomeModel.query.filter(IncomeModel.user_id==user_id).all()
    expenses = [expense.serialize() for expense in expenses_response]
    incomes = [income.serialize() for income in incomes_response]
    total_expenses = reduce(lambda a, b: a + b, [expense["value"] for expense in expenses], 0)
    total_income = reduce(lambda a, b: a + b, [income["value"] for income in incomes], 0)
    return { "balance": total_income - total_expenses }
