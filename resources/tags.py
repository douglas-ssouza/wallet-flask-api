from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel
from schemas import TagSchema

blp = Blueprint("Tags", "tags", description="Operations on tags.")


@blp.route("/tags")
class TagList(MethodView):
  @blp.response(200, TagSchema(many=True))
  def get(self):
    tags = TagModel.query.all()
    return tags
  
  @blp.arguments(TagSchema)
  @blp.response(201, TagSchema)
  def post(self, tag_data):
    tag = TagModel(**tag_data)
    try:
      db.session.add(tag)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return tag
  

@blp.route("/tags/<int:tag_id>")
class Tag(MethodView):
  @blp.response(200, TagSchema)
  def get(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    return tag
  
  @jwt_required()
  @blp.arguments(TagSchema)
  @blp.response(200, TagSchema)
  def put(self, tag_data, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    try:
      tag.name = tag_data["name"]
      db.session.add(tag)
      db.session.commit()
    except KeyError:
      abort(400, message="Make sure tag has a name.")
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    return tag
  
  @jwt_required()
  @blp.response(
    202,
    description="Deletes a tag if no item is tagged with it.",
    example={ "message": "Tag deleted." }
  )
  @blp.alt_response(404, description="Tag not found.")
  @blp.alt_response(400, description="Tags associated with 1 or more items can not be deleted.")
  def delete(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    
    if tag.incomes or tag.expenses:
      abort(400, message="Could not delete tag. Make sure tag is not associated with any items.")

    try:
      db.session.delete(tag)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return { "message": "Tag deleted." }