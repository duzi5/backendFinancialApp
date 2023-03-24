@app.route('/metas', methods=["POST"])
def insert_metas():
    meta = request.json['meta']
    title = request.json['title']
    family_id = request.json['family_id']
    metas = client.financialApp.metas
    metas.insert_one{
        "meta": meta,
        "title": title,
        "family_id": family_id
    }


