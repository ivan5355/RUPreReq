from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
import pandas as pd
import course_dependency as cd

app = Flask(__name__)

# Load the course data from the JSON file and extract the major field
df = pd.read_json('rutgers_courses.json')
df['major'] = df['courseString'].str.split(':').str[1]

@app.route('/api/graph/<major_number>')
def get_graph_data(major_number):
    """
    Endpoint to generate and return the graph data for a given major.

    This route processes the course data for a specific major (identified by 
    the `major_number`) and returns a graph structure with nodes (courses) 
    and edges (prerequisite dependencies).

    Args:
        major_number (str): The identifier for the major to get course data for.

    Returns:
        jsonify: A JSON response containing the graph data (nodes and edges) 
                 representing course dependencies.

    Raises:
        500 Internal Server Error: If there is an issue processing the graph data.
    """
    try:
        # Generate the adjacency matrix, course list, and prerequisite combinations
        adj_matrix, course_list, course_prereqs_combinations = cd.create_adjacency_matrix(major_number, df)

        # Initialize the structure for nodes and edges
        elements = {
            'nodes': [],
            'edges': []
        }

        # Create nodes from the course list
        for course_string, course_title in course_list.items():
            elements['nodes'].append({
                'data': {
                    'id': course_string,
                    'label': f"{course_string}: {course_title}"  # Display course string and title
                }
            })

        # Create edges based on the adjacency matrix
        for i, course_string in enumerate(course_list.keys()):
            for j, value in enumerate(adj_matrix[i]):
                if value == 1:  # If there is a prerequisite dependency (value == 1)
                    elements['edges'].append({
                        'data': {
                            'source': list(course_list.keys())[j],  # Prerequisite course
                            'target': course_string  # Dependent course
                        }
                    })

        # Return the JSON response with the graph data
        return jsonify(elements)

    except Exception as e:
        print(f"Error processing request for major {major_number}: {str(e)}")
        abort(500, description="Internal server error")


@app.route('/')
def serve_html():
    """
    Endpoint to serve the HTML page.

    This route serves the `index.html` file when the root URL is accessed.

    Returns:
        send_file: The `index.html` file to be served in the browser.
    """
    return send_file('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=7000)
