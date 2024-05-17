from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from functools import reduce
from db import db
from schemas import (
  ExpenseSchema,
  ExpenseUpdateSchema,
  ValueByOperationSchema,
  TotalValueSchema,
  TagAndExpenseSchema,
)
from models import ExpenseModel, UserModel, TagModel


blp = Blueprint("expenses", __name__, description="Operations on expenses")


@blp.route("/expenses")
class ExpenseList(MethodView):
  @jwt_required()
  @blp.response(200, ExpenseSchema(many=True))
  def get(self):
    return ExpenseModel.query.all()

  @jwt_required()
  @blp.arguments(ExpenseSchema)
  @blp.response(201, ExpenseSchema)
  def post(self, expense_data):
    expense = ExpenseModel(**expense_data)
    try:
      db.session.add(expense)
      db.session.commit()
    except SQLAlchemyError:
      abort(500, message="An error occurred while creating the expense.")
    return expense


@blp.route("/expenses/<string:expense_id>")
class Expense(MethodView):
  @jwt_required()
  @blp.response(200, ExpenseSchema)
  def get(self, expense_id):
    expense = ExpenseModel.query.get_or_404(expense_id)
    return expense

  @jwt_required()
  @blp.arguments(ExpenseUpdateSchema)
  @blp.response(200, ExpenseSchema)
  def put(self, expense_data, expense_id):
    expense = ExpenseModel.query.get_or_404(expense_id)
    try:
      expense.name = expense_data["name"]
      expense.value = expense_data["value"]
      expense.user_id = expense_data["user_id"]
      db.session.add(expense)
      db.session.commit()
    except KeyError:
      abort(400, message="Make sure expense has name, value and user_id fields.")
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return expense

  @jwt_required(fresh=True)
  def delete(self, expense_id):
    expense = ExpenseModel.query.get_or_404(expense_id)
    try:
      db.session.delete(expense)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return { "message": "Expense deleted." }, 200


@blp.route("/expenses/user/<string:user_id>")
class ExpenseUser(MethodView):
  @jwt_required()
  @blp.response(200, ExpenseSchema(many=True))
  def get(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    return user.expenses.all()


@blp.route("/expenses/user/<string:user_id>/total")
class ExpenseUserTotal(MethodView):
  @jwt_required()
  @blp.response(200, TotalValueSchema)
  def get(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    user_expenses = user.expenses.all()
    expenses = [expense.serialize() for expense in user_expenses]
    total = reduce(lambda a, b: a + b, [expense["value"] for expense in expenses], 0)
    return { "total": total, "user": user.serialize() }


@blp.route("/expenses/total")
class ExpenseTotal(MethodView):
  @jwt_required()
  @blp.response(200, TotalValueSchema)
  def get(self):
    response = ExpenseModel.query.all()
    expenses = [expense.serialize() for expense in response]
    total = reduce(lambda a, b: a + b, [expense["value"] for expense in expenses], 0)
    return { "total": total }


@blp.route("/expenses/value")
class ExpenseValue(MethodView):
  @jwt_required()
  @blp.arguments(ValueByOperationSchema)
  @blp.response(200, ExpenseSchema(many=True))
  def get(self, expense_data):
    response = ExpenseModel.query.all()
    expenses = [expense.serialize() for expense in response]
    if expense_data["operation"] == "over":
      return [expense for expense in expenses if expense["value"] >= expense_data["value"]]
    return [expense for expense in expenses if expense["value"] <= expense_data["value"]]


@blp.route("/expenses/<int:expense_id>/tag/<int:tag_id>")
class LinkTagsToExpense(MethodView):
  @jwt_required()
  @blp.response(201, ExpenseSchema)
  def post(self, expense_id, tag_id):
    expense = ExpenseModel.query.get_or_404(expense_id)
    tag = TagModel.query.get_or_404(tag_id)

    expense.tags.append(tag)

    try:
      db.session.add(expense)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return expense
  
  @jwt_required()
  @blp.response(200, TagAndExpenseSchema)
  def delete(self, expense_id, tag_id):
    expense = ExpenseModel.query.get_or_404(expense_id)
    tag = TagModel.query.get_or_404(tag_id)

    expense.tags.remove(tag)

    try:
      db.session.add(expense)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return { "message": "Tag removed from expense", "expense": expense, "tag": tag }