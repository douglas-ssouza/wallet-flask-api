from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from functools import reduce
from db import db
from schemas import (
  IncomeSchema,
  IncomeUpdateSchema,
  ValueByOperationSchema,
  TotalValueSchema,
  TagAndIncomeSchema,
)
from models import IncomeModel, UserModel, TagModel


blp = Blueprint("incomes", __name__, description="Operations on incomes")


@blp.route("/incomes")
class IncomeList(MethodView):
  @jwt_required()
  @blp.response(200, IncomeSchema(many=True))
  def get(self):
    return IncomeModel.query.all()

  @jwt_required()
  @blp.arguments(IncomeSchema)
  @blp.response(201, IncomeSchema)
  def post(self, income_data):
    income = IncomeModel(**income_data)
    try:
      db.session.add(income)
      db.session.commit()
    except SQLAlchemyError:
      abort(500, message="An erorr occurred while creating the income.")
    return income


@blp.route("/incomes/<int:income_id>")
class Income(MethodView):
  @jwt_required()
  @blp.response(200, IncomeSchema)
  def get(self, income_id):
    income = IncomeModel.query.get_or_404(income_id)
    return income

  @jwt_required()
  @blp.arguments(IncomeUpdateSchema)
  @blp.response(200, IncomeSchema)
  def put(self, income_data, income_id):
    income = IncomeModel.query.get_or_404(income_id)
    try:
      income.name = income_data["name"]
      income.value = income_data["value"]
      income.user_id = income_data["user_id"]
      db.session.add(income)
      db.session.commit()
    except KeyError:
      abort(400, message="Make sure income has name, value and user_id fields.")
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return income

  @jwt_required(fresh=True)
  def delete(self, income_id):
    income = IncomeModel.query.get_or_404(income_id)
    try:
      db.session.delete(income)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return { "message": "Income deleted." }, 200


@blp.route("/incomes/user/<string:user_id>")
class IncomeUser(MethodView):
  @jwt_required()
  @blp.response(200, IncomeSchema(many=True))
  def get(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    return user.incomes.all()


@blp.route("/incomes/user/<string:user_id>/total")
class IncomeUserTotal(MethodView):
  @jwt_required()
  @blp.response(200, TotalValueSchema)
  def get(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    user_incomes = user.incomes.all()
    incomes = [income.serialize() for income in user_incomes]
    total = reduce(lambda a, b: a + b, [income["value"] for income in incomes], 0)
    return { "total": total, "user": user.serialize() }  


@blp.route("/incomes/total")
class IncomeTotal(MethodView):
  @jwt_required()
  @blp.response(200, TotalValueSchema)
  def get(self):
    response = IncomeModel.query.all()
    incomes = [income.serialize() for income in response]
    total = reduce(lambda a, b: a + b, [income["value"] for income in incomes], 0)
    return { "total": total }


@blp.route("/incomes/value")
class IncomeValue(MethodView):
  @jwt_required()
  @blp.arguments(ValueByOperationSchema)
  @blp.response(200, IncomeSchema(many=True))
  def get(self, income_data):
    response = IncomeModel.query.all()
    incomes = [income.serialize() for income in response]
    if income_data["operation"] == "over":
      return [income for income in incomes if income["value"] >= income_data["value"]]
    return [income for income in incomes if income["value"] <= income_data["value"]]


@blp.route("/incomes/<string:income_id>/tag/<string:tag_id>")
class LinkTagsToIncome(MethodView):
  @jwt_required()
  @blp.response(201, IncomeSchema)
  def post(self, income_id, tag_id):
    income = IncomeModel.query.get_or_404(income_id)
    tag = TagModel.query.get_or_404(tag_id)

    income.tags.append(tag)

    try:
      db.session.add(income)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return income
  
  @jwt_required()
  @blp.response(200, TagAndIncomeSchema)
  def delete(post, income_id, tag_id):
    income = IncomeModel.query.get_or_404(income_id)
    tag = TagModel.query.get_or_404(tag_id)

    income.tags.remove(tag)

    try:
      db.session.add(income)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return { "message": "Tag removed from income", "income": income, "tag": tag }
