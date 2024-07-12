from pymongo import MongoClient

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client.blog_db

def create_schema():
    # Drop collections if they exist (optional, for fresh start)
    db.posts.drop()
    db.counters.drop()

    # Create the posts collection
    db.create_collection('posts')
    
    # Create the counters collection
    db.create_collection('counters')

    # Initialize the counters collection with a sequence for post IDs
    db.counters.insert_one({'_id': 'postid', 'seq': 0})

    # Define a schema for the posts collection
    db.command({
        'collMod': 'posts',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['title', 'content'],
                'properties': {
                    '_id': {
                        'bsonType': 'int',
                        'description': 'Post ID must be a sequential integer'
                    },
                    'title': {
                        'bsonType': 'string',
                        'description': 'Title of the post is required and must be a string'
                    },
                    'content': {
                        'bsonType': 'string',
                        'description': 'Content of the post is required and must be a string'
                    }
                }
            }
        },
        'validationAction': 'warn'
    })

    print("MongoDB schema created successfully.")

if __name__ == '__main__':
    create_schema()
