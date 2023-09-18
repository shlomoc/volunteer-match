import json
import openai
from collections import defaultdict

products_file = 'opportunities.json'
categories_file = 'categories.json'

delimiter = "####"
step_2_system_message_content = f"""
You will be provided with customer service queries. \
The most recent user query will be delimited with \
{delimiter} characters.
Output a python list of objects, where each object has \
the following format:
    'category': <one of Homeless Shelter, \
    Environmental Cleanup, \
    Youth Mentoring, \
    Animal Shelter, \
    Food Bank, \
    Community Development, \
    Education, \
    Mental Health, \
    Language Access, \
    Community Engagement, \
    Urban Gardening, \
    Arts Education, \
    Elderly Care, \
    Youth Sports >,
OR
    'opportunities': <a list of opportunities that must \
    be found in the allowed opportunities below>

Where the categories and opportunities must be found in \
the customer service query.
If a opportunity is mentioned, it must be associated with \
the correct category in the allowed opportunities list below.
If no opportunities or categories are found, output an \
empty list.
Only list opportunities and categories that have not already \
been mentioned and discussed in the earlier parts of \
the conversation.

Allowed opportunities: 
Homeless Shelter category:
Helping Hands Foundation
​
Environmental Cleanup category:
Eco Warriors
​
Youth Mentoring category:
Youth Empowerment League
​
Animal Shelter category:
Animal Guardians
​
Food Bank category:
Food for All
​
Community Development category:
Community Builders
​
Education category:
Virtual Tutoring Program
Tech for Good
​
Mental Health category:
Youth Helpline
​
Language Access category:
Remote Translation Services
​
Community Engagement category:
Online Community Support
​
Urban Gardening category:
Green Thumb Society
​
Arts Education category:
Creative Arts Center
​
Elderly Care category:
Senior Companions
​
Youth Sports category:
Community Sports League

Only output the list of objects, with nothing else.
"""

step_2_system_message = {'role':'system', 'content': step_2_system_message_content}    

step_4_system_message_content = f"""
    You are a customer service assistant that helps people find volunteer opportunities at non-profits. \
    Respond in a friendly and helpful tone, with VERY concise answers. \
    Make sure to ask the user relevant follow-up questions.
"""

step_4_system_message = {'role':'system', 'content': step_4_system_message_content}    

step_6_system_message_content = f"""
    You are an assistant that evaluates whether \
    customer service agent responses sufficiently \
    answer customer questions, and also validates that \
    all the facts the assistant cites from the volunteer opportunities \
    information are correct.
    The conversation history, volunteer opportunities information, user and customer \
    service agent messages will be delimited by \
    3 backticks, i.e. ```.
    Respond with a Y or N character, with no punctuation:
    Y - if the output sufficiently answers the question \
    AND the response correctly uses opportunity information
    N - otherwise

    Output a single letter only.
"""

step_6_system_message = {'role':'system', 'content': step_6_system_message_content}    


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message["content"]

def create_categories():
    categories_dict = {
      'Organization info': [
                'Name of organization',
                'Location',
                'category'],
      'Volunteer info':[
                'Start date',
                'End date',
                'Volunteering days',
                'skills'
                'description'],
      'General Inquiry':[
                'Location information'
                'Speak to a human']
    }
    
    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file)
        
    return categories_dict


def get_categories():
    with open(categories_file, 'r') as file:
            categories = json.load(file)
    return categories


def get_product_list():
    """
    Used in L4 to get a flat list of products
    """
    products = get_products()
    product_list = []
    for product in products.keys():
        product_list.append(product)
    
    return product_list

def get_products_and_category():
    """
    Used in L5
    """
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_info.get('nonprofit_organization'))
    
    return dict(products_by_category)

def get_products():
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def find_category_and_product(user_input,products_and_category):
    delimiter = "####"
    system_message = f"""
  You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of json objects, where each object has the following format:
        'category': <one of Homeless Shelter, Environmental Cleanup, Youth Mentoring, Animal Shelter, Food Bank, Community Development, \
    Education, Mental Health, Language Access, Community Engagement, Urban Gardening, Arts Education, Elderly Care, Youth Sports >,
    OR
        'opportunity': <a list of opportunities that must be found in the allowed opportunities below>
    Where the categories and opportunities must be found in the customer service query.
    If an opportunity is mentioned, it must be associated with the correct category in the allowed opportunities list below.
    If no opportunities or categories are found, output an empty list.

    The allowed opportunities are provided in JSON format.
    The keys of each item represent the category.
    The values of each item is a list of opportunities that are within that category.
    Allowed opportunities: {products_and_category}
    
    """
    messages =  [  
    {'role':'system', 'content': system_message},    
    {'role':'user', 'content': f"{delimiter}{user_input}{delimiter}"},  
    ] 
    return get_completion_from_messages(messages)

def find_category_and_product_only(user_input,products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of json objects, where each object has the following format:
        'category': <one of Homeless Shelter, Environmental Cleanup, Youth Mentoring, Animal Shelter, Food Bank, Community Development, \
    Education, Mental Health, Language Access, Community Engagement, Urban Gardening, Arts Education, Elderly Care, Youth Sports >,
    OR
        'opportunity': <a list of opportunities that must be found in the allowed opportunities below>
    Where the categories and opportunities must be found in the customer service query.
    If an opportunity is mentioned, it must be associated with the correct category in the allowed opportunities list below.
    If no opportunities or categories are found, output an empty list.
    This is important: Only output the list of objects, nothing else. Do not output anything after the list of objects.
            
    Allowed opportunities: 
Homeless Shelter category:
Helping Hands Foundation
​
Environmental Cleanup category:
Eco Warriors
​
Youth Mentoring category:
Youth Empowerment League
​
Animal Shelter category:
Animal Guardians
​
Food Bank category:
Food for All
​
Community Development category:
Community Builders
​
Education category:
Virtual Tutoring Program
Tech for Good
​
Mental Health category:
Youth Helpline
​
Language Access category:
Remote Translation Services
​
Community Engagement category:
Online Community Support
​
Urban Gardening category:
Green Thumb Society
​
Arts Education category:
Creative Arts Center
​
Elderly Care category:
Senior Companions
​
Youth Sports category:
Community Sports League
    

    """
    messages =  [  
    {'role':'system', 'content': system_message},    
    {'role':'user', 'content': f"{delimiter}{user_input}{delimiter}"},  
    ] 
    return get_completion_from_messages(messages)

def get_products_from_query(user_msg):
    """
    Code from L5, used in L8
    """
    products_and_category = get_products_and_category()
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of json objects, where each object has the following format:
        'category': <one of Homeless Shelter, Environmental Cleanup, Youth Mentoring, Animal Shelter, Food Bank, Community Development, \
    Education, Mental Health, Language Access, Community Engagement, Urban Gardening, Arts Education, Elderly Care, Youth Sports >,
    OR
        'opportunity': <a list of opportunities that must be found in the allowed opportunities below>
    Where the categories and opportunities must be found in the customer service query.
    If an opportunity is mentioned, it must be associated with the correct category in the allowed opportunities list below.
    If no opportunities or categories are found, output an empty list.

    The allowed opportunities are provided in JSON format.
    The keys of each item represent the category.
    The values of each item is a list of opportunities that are within that category.
    Allowed opportunities: {products_and_category}

    """
    
    messages =  [  
    {'role':'system', 'content': system_message},    
    {'role':'user', 'content': f"{delimiter}{user_msg}{delimiter}"},  
    ] 
    category_and_product_response = get_completion_from_messages(messages)
    
    return category_and_product_response


# product look up (either by category or by product within category)
def get_product_by_name(name):
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    products = get_products()
    return [product for product in products.values() if product["category"] == category]

def get_mentioned_product_info(data_list):
    """
    Used in L5 and L6
    """
    product_info_l = []

    if data_list is None:
        return product_info_l

    for data in data_list:
        try:
            if "products" in data:
                products_list = data["opportunities"]
                for product_name in products_list:
                    product = get_product_by_name(product_name)
                    if product:
                        product_info_l.append(product)
                    else:
                        print(f"Error: Opportunity '{product_name}' not found")
            elif "category" in data:
                category_name = data["category"]
                category_products = get_products_by_category(category_name)
                for product in category_products:
                    product_info_l.append(product)
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return product_info_l



def read_string_to_list(input_string):
    if input_string is None:
        return None

    try:
        #input_string = get_json_from_string(input_string)
        #print(input_string)
        input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
        #print(input_string)
        data = json.loads(input_string)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None
    
def get_json_from_string(string):
  """Gets the JSON portion of a string.

  Args:
    string: The string to get the JSON portion from.

  Returns:
    The JSON portion of the string.
  """

  start_index = string.find('[')
  end_index = string.rfind(']')

  if start_index == -1 or end_index == -1:
    return None

  return string[start_index:end_index + 1]

def generate_output_string(data_list):
    output_string = ""

    if data_list is None:
        return output_string

    for data in data_list:
        try:
            if "opportunity" in data:
                products_list = data["opportunity"]
                for product_name in products_list:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: opportunity '{product_name}' not found")
            elif "category" in data:
                category_name = data["category"]
                category_products = get_products_by_category(category_name)
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string

# Example usage:
#product_information_for_user_message_1 = generate_output_string(category_and_product_list)
#print(product_information_for_user_message_1)

def answer_user_msg(user_msg,product_info):
    """
    Code from L5, used in L6
    """
    delimiter = "####"
    system_message = f"""
    You are a customer service assistant for Nonprofit volunteering information. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow up questions.
    """
    # user_msg = f"""
    # tell me about the Youth Empowerment League . Also what tell me about your Environmental Cleanup"""
    messages =  [  
    {'role':'system', 'content': system_message},   
    {'role':'user', 'content': f"{delimiter}{user_msg}{delimiter}"},  
    {'role':'assistant', 'content': f"Relevant opportunity information:\n{product_info}"},   
    ] 
    response = get_completion_from_messages(messages)
    return response

def create_products():
    """
        Create products dictionary and save it to a file named products.json
    """
    # product information
    # fun fact: all these products are fake and were generated by a language model
    products = {
    "Helping Hands Foundation": 
    {
      "nonprofit_organization": "Helping Hands Foundation",
      "location": "New York City",
      "category": "Homeless Shelter",
      "volunteering_days": ["Monday", "Wednesday", "Saturday"],
      "description": "Join us at the Helping Hands Shelter to provide support, meals, and resources to individuals experiencing homelessness.",
      "group_size": "10-15",
      "start_date": "2023-07-01",
      "end_date": "2023-12-31",
      "desired_skills": ["Communication", "Empathy"],
      "volunteer_type": "In-person"
    },
    "Eco Warriors":
    {
      "nonprofit_organization": "Eco Warriors",
      "location": "San Francisco",
      "category": "Environmental Cleanup",
      "volunteering_days": ["Saturday"],
      "description": "Make a difference in the local environment by participating in our monthly beach and park cleanup events.",
      "group_size": "20-30",
      "start_date": "2023-07-15",
      "end_date": "2024-06-30",
      "desired_skills": ["Sustainability", "Teamwork"],
      "volunteer_type": "In-person"
    },
    "Youth Empowerment League":
    {
      "nonprofit_organization": "Youth Empowerment League",
      "location": "Chicago",
      "category": "Youth Mentoring",
      "volunteering_days": ["Tuesday", "Thursday"],
      "description": "Become a mentor and inspire young individuals through educational, career, and personal development activities.",
      "group_size": "5-10",
      "start_date": "2023-08-01",
      "end_date": "2023-12-15",
      "desired_skills": ["Mentoring", "Patience"],
      "volunteer_type": "In-person"
    },
    "Animal Guardians":
    {
      "nonprofit_organization": "Animal Guardians",
      "location": "Los Angeles",
      "category": "Animal Shelter",
      "volunteering_days": ["Monday", "Tuesday", "Friday"],
      "description": "Assist in caring for shelter animals by providing feeding, grooming, and exercise, and help find them forever homes.",
      "group_size": "1-5",
      "start_date": "2023-07-01",
      "end_date": "2023-09-30",
      "desired_skills": ["Animal Handling", "Compassion"],
      "volunteer_type": "In-person"
    },
    "Food for All":
    {
      "nonprofit_organization": "Food for All",
      "location": "Seattle",
      "category": "Food Bank",
      "volunteering_days": ["Monday", "Wednesday", "Friday", "Saturday"],
      "description": "Help sort, package, and distribute food to individuals and families in need through our local food bank.",
      "group_size": "10-20",
      "start_date": "2023-07-01",
      "end_date": "2024-01-31",
      "desired_skills": ["Organizational Skills", "Teamwork"],
      "volunteer_type": "In-person"
    },
    "Community Builders":
    {
      "nonprofit_organization": "Community Builders",
      "location": "New York City",
      "category": "Community Development",
      "volunteering_days": ["Tuesday", "Thursday", "Friday"],
      "description": "Get involved in community projects, such as neighborhood cleanups, urban gardening, and public space enhancement.",
      "group_size": "5-10",
      "start_date": "2023-08-15",
      "end_date": "2023-11-30",
      "desired_skills": ["Collaboration", "Creativity"],
      "volunteer_type": "In-person"
    },
    "Virtual Tutoring Program":
    {
      "nonprofit_organization": "Virtual Tutoring Program",
      "location": "Remote",
      "category": "Education",
      "volunteering_days": ["Flexible"],
      "description": "Support students from underserved communities through virtual tutoring sessions in various subjects and grade levels.",
      "group_size": "1-1",
      "start_date": "2023-07-01",
      "end_date": "2023-12-31",
      "desired_skills": ["Teaching", "Patience"],
      "volunteer_type": "Virtual"
    },
    "Tech for Good":
    {
      "nonprofit_organization": "Tech for Good",
      "location": "Remote",
      "category": "Technology Education",
      "volunteering_days": ["Flexible"],
      "description": "Share your tech expertise remotely by mentoring students and teaching them valuable digital skills and programming.",
      "group_size": "1-1",
      "start_date": "2023-07-15",
      "end_date": "2024-06-30",
      "desired_skills": ["Programming", "Communication"],
      "volunteer_type": "Virtual"
    },
    "Youth Helpline":
    {
      "nonprofit_organization": "Youth Helpline",
      "location": "Remote",
      "category": "Mental Health",
      "volunteering_days": ["Flexible"],
      "description": "Provide virtual support and counseling to young individuals who are in need of emotional assistance and guidance.",
      "group_size": "1-1",
      "start_date": "2023-08-01",
      "end_date": "2023-12-15",
      "desired_skills": ["Active Listening", "Empathy"],
      "volunteer_type": "Virtual"
    },
    "Remote Translation Services":
    {
      "nonprofit_organization": "Remote Translation Services",
      "location": "Remote",
      "category": "Language Access",
      "volunteering_days": ["Flexible"],
      "description": "Help bridge language barriers by offering remote translation services to nonprofit organizations and communities.",
      "group_size": "1-1",
      "start_date": "2023-07-01",
      "end_date": "2023-09-30",
      "desired_skills": ["Bilingualism", "Cultural Sensitivity"],
      "volunteer_type": "Virtual"
    },
    "Online Community Support":
    {
      "nonprofit_organization": "Online Community Support",
      "location": "Remote",
      "category": "Community Engagement",
      "volunteering_days": ["Flexible"],
      "description": "Engage with online communities, provide emotional support, share resources, and foster a positive online environment.",
      "group_size": "1-1",
      "start_date": "2023-07-01",
      "end_date": "2024-01-31",
      "desired_skills": ["Communication", "Compassion"],
      "volunteer_type": "Virtual"
    },
    "Green Thumb Society":
    {
      "nonprofit_organization": "Green Thumb Society",
      "location": "Portland",
      "category": "Urban Gardening",
      "volunteering_days": ["Saturday"],
      "description": "Join us in creating sustainable and vibrant urban gardens to promote healthy eating and environmental awareness.",
      "group_size": "5-10",
      "start_date": "2023-08-15",
      "end_date": "2023-11-30",
      "desired_skills": ["Gardening", "Sustainability"],
      "volunteer_type": "In-person"
    },
    "Creative Arts Center":
    {
      "nonprofit_organization": "Creative Arts Center",
      "location": "Boston",
      "category": "Arts Education",
      "volunteering_days": ["Wednesday", "Friday"],
      "description": "Inspire creativity and artistic expression in youth by assisting with art classes and organizing exhibitions.",
      "group_size": "5-10",
      "start_date": "2023-08-01",
      "end_date": "2023-12-15",
      "desired_skills": ["Artistic Skills", "Patience"],
      "volunteer_type": "In-person"
    },
    "Senior Companions":
    {
      "nonprofit_organization": "Senior Companions",
      "location": "Miami",
      "category": "Elderly Care",
      "volunteering_days": ["Monday", "Tuesday", "Thursday"],
      "description": "Spend quality time with seniors, engage in conversations, and assist with daily activities to combat loneliness.",
      "group_size": "1-5",
      "start_date": "2023-07-01",
      "end_date": "2023-09-30",
      "desired_skills": ["Compassion", "Patience"],
      "volunteer_type": "In-person"
    },
    "Community Sports League":
    {
      "nonprofit_organization": "Community Sports League",
      "location": "Dallas",
      "category": "Youth Sports",
      "volunteering_days": ["Saturday", "Sunday"],
      "description": "Coach and mentor youth in various sports, promoting teamwork, discipline, and a healthy lifestyle.",
      "group_size": "10-15",
      "start_date": "2023-07-01",
      "end_date": "2023-12-31",
      "desired_skills": ["Sports Knowledge", "Leadership"],
      "volunteer_type": "In-person"
    }
    }

    products_file = 'opportunities.json'
    with open(products_file, 'w') as file:
        json.dump(products, file)
        
    return products