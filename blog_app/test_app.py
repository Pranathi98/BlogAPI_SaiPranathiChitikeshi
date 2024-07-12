import unittest

from flask import json

from app import app, counters_collection, posts_collection, users_collection


class BlogAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.app = app
        cls.app_context = app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        # Reset the database before each test
        posts_collection.drop()
        counters_collection.drop()
        counters_collection.insert_one({'_id': 'postid', 'seq': 0})

    def tearDown(self):
        # Clean up the database after each test
        posts_collection.drop()
        counters_collection.drop()

    def setUp(self):
        # Reset the database before each test
        posts_collection.drop()
        counters_collection.drop()
        users_collection.drop()
        counters_collection.insert_one({'_id': 'postid', 'seq': 0})

        # Sign up a test user
        response = self.client.post('/signup', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Log in the test user
        response = self.client.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.access_token = data['access_token']

    def tearDown(self):
        # Clean up the database after each test
        posts_collection.drop()
        counters_collection.drop()
        users_collection.drop()
    
    #create test user
    def test_create_post(self):
        response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        },data=json.dumps({
            'title': 'Test Post',
            'content': 'This is a test post.'
        }), content_type='application/json')

        #compare and verify
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['content'], 'This is a test post.')

    #get all blogs
    def test_get_posts(self):
        self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Test Post 1',
            'content': 'This is the first test post.'
        }), content_type='application/json')
        self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Test Post 2',
            'content': 'This is the second test post.'
        }), content_type='application/json')

        response = self.client.get('/posts', headers={
        'Authorization': f'Bearer {self.access_token}'
    })
        #compare and verify
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    #get blog by id
    def test_get_post(self):
        post_response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Test Post',
            'content': 'This is a test post.'
        }), content_type='application/json')
        post_data = json.loads(post_response.data)
        post_id = post_data['_id']

        response = self.client.get(f'/posts/{post_id}', headers={
        'Authorization': f'Bearer {self.access_token}'
    })
        #compare and verify
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Test Post')

    #update blog
    def test_update_post(self):
        post_response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Old Title',
            'content': 'Old content.'
        }), content_type='application/json')
        post_data = json.loads(post_response.data)
        post_id = post_data['_id']

        response = self.client.put(f'/posts/{post_id}', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Updated Title',
            'content': 'Updated content.'
        }), content_type='application/json')
        #compare and verify
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['content'], 'Updated content.')

    #delete blog by id
    def test_delete_post(self):
        post_response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Test Post to Delete',
            'content': 'This post will be deleted.'
        }), content_type='application/json')
        post_data = json.loads(post_response.data)
        post_id = post_data['_id']

        response = self.client.delete(f'/posts/{post_id}', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        #compare and verify
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], f'Post with ID {post_id} has been deleted successfully')

        response = self.client.get(f'/posts/{post_id}', headers={
        'Authorization': f'Bearer {self.access_token}'
        })
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("404 Not Found: "))
        self.assertIn(f"Post with ID {post_id} not found", data['error'])
        
    #create blog with missing value
    def test_create_post_missing_title(self):
        response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'content': 'This is a post without a title.'
        }), content_type='application/json')
        #compare and verify
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("400 Bad Request: "))
        self.assertIn("Missing 'title' or 'content'", data['error'])

    #create blog with missing value
    def test_create_post_missing_content(self):
        response = self.client.post('/posts', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'This is a post without a title.'
        }), content_type='application/json')
        #compare and verify
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("400 Bad Request: "))
        self.assertIn("Missing 'title' or 'content'", data['error'])

    #find blog by id which does not exists
    def test_get_post_not_found(self):
        response = self.client.get('/posts/99999999', headers={
        'Authorization': f'Bearer {self.access_token}'
    })
        #compare and verify
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("404 Not Found: "))
        self.assertIn("Post with ID 99999999 not found", data['error'])

    #update blog by id which does not exists
    def test_update_post_not_found(self):
        response = self.client.put('/posts/99999999', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, data=json.dumps({
            'title': 'Non-existent Post'
        }), content_type='application/json')
        #compare and verify
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("404 Not Found: "))
        self.assertIn("Post with ID 99999999 not found", data['error'])

    #delete blog by id which does not exists
    def test_delete_post_not_found(self):
        response = self.client.delete('/posts/99999999', headers={
            'Authorization': f'Bearer {self.access_token}'
        })
        #compare and verify
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertTrue(data['error'].startswith("404 Not Found: "))
        self.assertIn("Post with ID 99999999 not found", data['error'])

#main
if __name__ == '__main__':
    unittest.main()
