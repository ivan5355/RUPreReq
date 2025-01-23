import re
import pandas as pd
import numpy as np
import itertools

# Load the data 
df = pd.read_json('rutgers_courses.json')

# Extract major from courseString
df['major'] = df['courseString'].str.split(':').str[1]

def find_combinations(nested_course_lists):
    """
    Find all possible combinations of courses from a list of nested course lists.

    Args:
        nested_course_lists (list of list): A list where each element is a list of course options.

    Returns:
        list of list of tuples: A list of combinations for each set of course lists.
    """
    result = []
    for course_lists in nested_course_lists:
        combinations = list(itertools.product(*course_lists))
        result.append(combinations)
    return result

def parse_prerequisites(preReqNotes):
    """
    Parse the prerequisites from the preReqNotes column and return a list of course combinations
    based on logical structures like 'OR' and 'AND'.

    Args:
        preReqNotes (str): The prerequisites notes string for a course.

    Returns:
        list of list of list: A list representing prerequisite relationships in logical groups.
    """
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

def flatten_combinations(nested_combinations):
    """
    Flatten a list of nested combinations into a single list of all possible combinations.

    Args:
        nested_combinations (list of list): A list of nested course combinations.

    Returns:
        list: A flattened list of all possible course combinations.
    """
    flattened_list = []
    for group in nested_combinations:
        for combo in group:
            flattened_list.append(combo)
    return flattened_list

def extract_external_prereqs_with_titles(major_courses):
    """
    Extract prerequisites from courses outside of the major, and return a dictionary of external 
    prerequisites with their titles.

    Args:
        major_courses (DataFrame): A DataFrame containing courses from a specific major.

    Returns:
        dict: A dictionary where keys are course strings and values are the course titles.
    """
    # Collect all major course
    major_course_strings = major_courses['courseString']

    # Initialize a set for external prerequisites
    external_prereqs = set()

    for index, row in major_courses.iterrows():
        # Prereqs for the current course
        prerequisites = row['flattened_prerequisite_codes']  

        # Process each prerequisite combination
        for prereq_combo in prerequisites:
            for prereq in prereq_combo:
                # Add to external prereqs if not part of the major courses
                if prereq not in major_course_strings:
                    external_prereqs.add(prereq)

    external_prereqs_dict = {}
    
    for prereq in external_prereqs:
        # Search the DataFrame for the prerequisite's title by first accessing the row where the prereq is
        matching_row = df.loc[df['courseString'] == prereq]
        
        # Retrieve the title if a match exists
        if not matching_row.empty:
            external_prereqs_dict[prereq] = matching_row.iloc[0]['title']

    return external_prereqs_dict

def create_adjacency_matrix(major_number, df):
    """
    Create an adjacency matrix representing course prerequisites for a specified major.

    Args:
        major_number (str): The major code to filter the courses.
        df (DataFrame): The DataFrame containing all courses.

    Returns:
        tuple: A tuple containing the adjacency matrix (numpy array), a dictionary of course strings
               to titles, and a dictionary of course prerequisite combinations.
    """
    df['prerequisite_codes'] = df['preReqNotes'].apply(parse_prerequisites)
    df['prerequisite_codes'] = df['prerequisite_codes'].apply(find_combinations)
    df['flattened_prerequisite_codes'] = df['prerequisite_codes'].apply(flatten_combinations)

    # Filter courses for the specified major
    major_courses = df[df['major'] == major_number]
    major_courses = major_courses[
        ~major_courses['courseString'].str.split(':').str[2].str.startswith(('5', '6', '7', '8', '9'))
    ]
   
    course_prereqs_combinations = {}

    # Store each course and its prereqs
    for index, row in major_courses.iterrows():
        course = row['courseString']
        prereqs = row['flattened_prerequisite_codes']
        course_prereqs_combinations[course] = prereqs

    # Create a dictionary for course strings and titles
    course_list = {}
    for index, row in major_courses.iterrows():
        course_list[row['courseString']] = row['title']

    # external_prereqs is another dictionary with course strings and titles
    external_prereqs = extract_external_prereqs_with_titles(major_courses)

    # Extend course_list with external_prereqs
    course_list.update(external_prereqs)

    # Create an empty adjacency matrix
    n = len(course_list)
    adj_matrix = np.zeros((n, n))
    
    # Create a mapping of course strings to matrix indices
    course_to_index = {}
    for idx, course in enumerate(course_list.keys()):
        course_to_index[course] = idx

    # Fill the adjacency matrix
    for index, row in major_courses.iterrows():
        course = row['courseString']
        prerequisites = row['flattened_prerequisite_codes']
        
        for prereq_combo in prerequisites:
            for prereq in prereq_combo:
                if prereq in course_to_index:  
                    prereq_idx = course_to_index[prereq]
                    course_idx = course_to_index[course]
                    adj_matrix[prereq_idx][course_idx] = 1  

    return adj_matrix, course_list, course_prereqs_combinations

if __name__ == "__main__":
    adj_matrix, course_list, course_prereqs_combinations = create_adjacency_matrix('198', df)
