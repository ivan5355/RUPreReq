import pprint
from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
import pandas as pd
import course_dependency as cd
from pprint import pprint


app = Flask(__name__)

# Load the course data from the JSON file and extract the major field
df = pd.read_json('rutgers_courses.json')
df['major'] = df['courseString'].str.split(':').str[1]


@app.route('/')
def serve_html():
    """
    Endpoint to serve the HTML page.

    This route serves the `index.html` file when the root URL is accessed.

    Returns:
        send_file: The `index.html` file to be served in the browser.
    """
    return send_file('index.html')

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




def get_course_prereqs(major_number, course_string):
    """
    Get prerequisite combinations for a specific course.
    
    Args:
        major_number (str): The major code (e.g., '198' for Computer Science)
        course_string (str): The course code. Accepts '01:198:112' or compact '01198112'.
        
    Returns:
        JSON response containing:
        - prerequisite_combinations: List of prerequisite combinations
    """

    # Get course data
    adj_matrix, course_list, course_prereqs_combinations = cd.create_adjacency_matrix(major_number, df)

    # Normalize compact course codes like '01198112' to '01:198:112'
    if ':' not in course_string and len(course_string) == 8 and course_string.isdigit():
        course_string = f"{course_string[:2]}:{course_string[2:5]}:{course_string[5:]}"

    # Look up combinations for the requested course
    course_prereqs = course_prereqs_combinations.get(course_string, [])
    
    # Prepare response data
    response_data = {
        'prerequisite_combinations': []
    }

    for combo in course_prereqs:
        group = []
        for course in combo:
            group.append(course)
        response_data['prerequisite_combinations'].append(group)
    
    return response_data

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/test')
def test():
    return jsonify({"message": "Flask app is running", "courses_loaded": len(df) if 'df' in globals() else 0}), 200

if __name__ == '__main__':
    app.run(debug=True, port=7000)




 