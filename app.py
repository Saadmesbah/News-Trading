from flask import Flask, render_template, request, jsonify
from Database.elastic import (
    get_all, get_by_date, update_sentiment,
    delete_sentiment, search_by_keyword, create_index
)

app = Flask(__name__)
create_index()

# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    docs = get_all()
    return render_template('index.html', docs=docs)

# ── CRUD API ──────────────────────────────────────────────────────────────────

@app.route('/api/all', methods=['GET'])
def api_get_all():
    return jsonify(get_all())

@app.route('/api/search', methods=['GET'])
def api_search():
    keyword = request.args.get('keyword', '')
    date    = request.args.get('date', '')
    if keyword:
        return jsonify(search_by_keyword(keyword))
    if date:
        return jsonify(get_by_date(date))
    return jsonify(get_all())

@app.route('/api/update/<doc_id>', methods=['PUT'])
def api_update(doc_id):
    data = request.json
    update_sentiment(doc_id, data)
    return jsonify({"status": "updated", "id": doc_id})

@app.route('/api/delete/<doc_id>', methods=['DELETE'])
def api_delete(doc_id):
    delete_sentiment(doc_id)
    return jsonify({"status": "deleted", "id": doc_id})

if __name__ == '__main__':
    app.run(debug=True)