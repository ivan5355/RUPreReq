import itertools
import re
import pandas as pd
import numpy as np

import networkx as nx

# Initialize a directed graph
course_graph = nx.DiGraph()

#Load the data 
df = pd.read_json('rutgers_courses.json')

# Extract major from courseString
df['major'] = df['courseString'].str.split(':').str[1]

# Function to find all combinations of courses
def find_combinations(nested_course_lists):

    result = []

    for course_lists in nested_course_lists:
        combinations = list(itertools.product(*course_lists))
        result.append(combinations)

    return result
   
# Extracts prerequisite relationships from the preReqNotes column, identifying prereqs based on logical structures like "OR" or "AND".
def parse_prerequisites(preReqNotes):

    # Remove HTML tags
    clean_notes = re.sub(r"<[^>]+>", "", preReqNotes)

    # Split by 'OR' to identify different main groups
    or_groups = []
    for group in clean_notes.split("OR"):
        or_groups.append(group.strip())

    prerequisites = []
    
    # Process each OR group
    for group in or_groups:
        and_courses = []
        
        # Split by 'and' to identify AND conditions within each group
        and_conditions = group.split("and")
        
        for condition in and_conditions:

            # Find all course numbers in the condition
            courses = re.findall(r'\b\d{2}:\d{3}:\d{3}\b', condition)
            
            if courses:  # Only add non-empty results
                and_courses.append(courses)
        
        # Append the AND conditions for each OR group
        if and_courses:
            prerequisites.append(and_courses)
    
    return prerequisites

# Flatten the prerequisite combinations into a single list
def flatten_combinations(nested_combinations):

    flattened_list = []

    for group in nested_combinations:
        for combo in group:
            flattened_list.append(combo)

    return flattened_list

# Generates all possible prerequisite combinations
def print_prereqs(major_number, df):

    # Filter the DataFrame for the specified major
    major_courses = df[df['major'] == major_number]
    major_courses = major_courses[
        ~major_courses['courseString'].str.split(':').str[2].str.startswith(('5', '6', '7', '8', '9'))
    ]
    
    # Print the courseString and flattened prerequisites
    for index, row in major_courses.iterrows():
        course_string = row['courseString']
        flattened_prereqs = row['flattened_prerequisite_codes']
        print(f"{course_string}: {flattened_prereqs}")
        print('\n')
        
    
#extract prereqs that are not part of the major
def extract_external_prereqs(major_courses, df):
 
    #avoids duplicates
    external_prereqs = set() 

    #iterate through each row
    for index, row in major_courses.iterrows():

        prerequisites = row['flattened_prerequisite_codes']
        
        #loop through prereqs of major and check if the 
        for prereq_combo in prerequisites:
            for prereq in prereq_combo:

                # Check if the prerequisite is in the major courses
                if prereq not in major_courses['courseString'].values:
                    external_prereqs.add(prereq)

    return list(external_prereqs)
    

def create_adjacency_matrix(major_number, df):

    df['prerequisite_codes'] = df['preReqNotes'].apply(parse_prerequisites)
    df['prerequisite_codes'] = df['prerequisite_codes'].apply(find_combinations)
    df['flattened_prerequisite_codes'] = df['prerequisite_codes'].apply(flatten_combinations)

    # Filter courses for the specified major
    major_courses = df[df['major'] == major_number]
    major_courses = major_courses[
        ~major_courses['courseString'].str.split(':').str[2].str.startswith(('5', '6', '7', '8', '9'))
    ]

    # Get list of all course strings in the major
    course_list = major_courses['courseString'].tolist()
    
    # Create an empty adjacency matrix
    n = len(course_list)
    adj_matrix = np.zeros((n, n))
    
    # Create a mapping of course strings to matrix indices
    course_to_index = {}
    for idx, course in enumerate(course_list):
        course_to_index[course] = idx


    # Fill the adjacency matrix
    #Loop through rows
    for index, row in major_courses.iterrows():

        #Course that you are searching prereqs for
        course = row['courseString']

        #
        prerequisites = row['flattened_prerequisite_codes']
        
        # Lopp through each prereq combo
        for prereq_combo in prerequisites:
            
            #Loop through each prereq in combo and 
            for prereq in prereq_combo:
                if prereq in course_to_index:  
                    
                    prereq_idx = course_to_index[prereq]
                    course_idx = course_to_index[course]
                    adj_matrix[prereq_idx][course_idx] = 1  

    # Extract external prerequisites
    external_prereqs = extract_external_prereqs(major_courses, df)
    print(external_prereqs)

    return adj_matrix, course_list, external_prereqs

if __name__ == "__main__":

    adj_matrix = create_adjacency_matrix('198', df)
    print(adj_matrix)

