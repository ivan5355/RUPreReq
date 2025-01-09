from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
import pandas as pd
import numpy as np
import course_dependency as cd

app = Flask(__name__)
CORS(app)

# Load the course data
df = pd.read_json('rutgers_courses.json')
df['major'] = df['courseString'].str.split(':').str[1]

# get the graph data
@app.route('/api/graph/<major_number>')
def get_graph_data(major_number):
    
    try:
        
        adj_matrix, course_list, external_prereqs = cd.create_adjacency_matrix(major_number, df)

        elements = {
            'nodes': [],
            'edges': []
        }

        # Create nodes
        for course in course_list:
            elements['nodes'].append({
                'data': {
                    'id': course,
                    'label': course
                }
            })

        # Create edges based on the adjacency matrix
        for i, course in enumerate(course_list):
            for j, value in enumerate(adj_matrix[i]):
                
                if value == 1:  
                    elements['edges'].append({
                        'data': {
                            'source': course_list[j],
                            'target': course
                        }
                    })


        return jsonify(elements)

    except Exception as e:
        print(f"Error processing request for major {major_number}: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/')
def serve_html():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000) 