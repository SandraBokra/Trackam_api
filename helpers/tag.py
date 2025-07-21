from flask_jwt_extended import jwt_required
from flask import request
from config.db import db


from flask import request
from models.trackam import Tag



def CreateTag():
    reponse={}
    data = request.get_json()
    name = data.get("name")
    single_tag = Tag.query.filter_by(name=name).first()
    if single_tag :
        return {"message": "Ce tag existe deja"}, 400

    new_tag = Tag()
    new_tag.name = name

    db.session.add(new_tag)
    db.session.commit()

    reponse['status'] = 'success'
    return reponse


def GetAllTag():
    tags = Tag.query.all()

    result = []
    for tag in tags:
        result.append({
            'uid': tag.uid,
            'name': tag.name
        })

    return {"tags": result}, 200



def GetSingleTag():
    tag_id = request.json.get("uid")
    if not tag_id:
        return {"message": "ID requis"}, 400

    tag = Tag.query.filter_by(uid=tag_id).first()
    if not tag:
        return {"message": "Tag non trouvé"}, 404

    return ({"tag": {
        'uid': tag.uid,
        'name': tag.name
    }}, 200)


def DeleteTag():
    tag_id = request.json.get("uid")
    if not tag_id:
        return {"message": "ID requis"}, 400

    new_tag = Tag.query.filter_by(uid=tag_id).first()
    if not new_tag:
        return {"message": "Tag non trouvé"}, 404

    db.session.delete(new_tag)
    db.session.commit()
    return {"message": "Tag supprimé"}



def UpdateTag():
    name=request.json.get("name") 
    uid = request.json.get("uid") 
    if not uid or not name :
        return {"message": "ID ou name du tag requis"}, 400
    update_tag = Tag.query.filter_by(uid=uid).first()
    if not update_tag:
        return {"message": "Tag non trouvé"}, 404
    
    update_tag.name =name
    db.session.add(update_tag)
    db.session.commit()
       
    return {"message": "Tag mis à jour avec succès"}, 200
