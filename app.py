from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import json
from ai import get_completion_stream
from utils import query_tinybird

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    # Query for the graph: sum of calories/macros per day
    sql = """
    SELECT 
        toString(day) as date,
        sum(energy_kcal) as calories,
        sum(carbs_g) as carbs,
        sum(fat_g) as fat,
        sum(protein_g) as protein
    FROM servings_apr_25
    GROUP BY day
    ORDER BY day
    """
    try:
        data = query_tinybird(sql)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sql', methods=['POST'])
def run_sql():
    # Manual SQL endpoint
    query = request.json.get('query')
    try:
        data = query_tinybird(query)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')

    def generate():
        """Generator function to stream Server-Sent Events"""
        try:
            for event in get_completion_stream(user_query):
                # Format as SSE: data: {json}\n\n
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            # Send error event
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return Response(stream_with_context(generate()), 
                   mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
