Dependencies:
    Flask: A lightweight WSGI web application framework.
    Flask-PyMongo: Flask extension for MongoDB integration.
    Flask-JWT-Extended: Extension for JSON Web Token (JWT) handling.
    python-dotenv: To manage environment variables.
    requests: For making HTTP requests to test endpoints.
    pytest: Testing framework.
    Flask-Testing: Extension for unit testing Flask applications.
    You can also install requirements.txt using pip install

SetUp :
    - Clone or dolwnload the project repository/folder.
    - Open it in VS code.
    - Adjust the .env file accordingly with correct values and change the url according to the required environment.
    - Then use falsk run or python app.py to run the application.
    - You can test the endpoins using postman.
    - Install postman and start a new session and enter the correct url and port number.
    - First run the signup/login endpoint by passing json data in the body where a bearer  token will be generated.
    - Use that token to pass in the authentication tab as the bearer token and send the required requests you want to pass to test i.e., get/post/update/delete.
    - You need to pass the json data in the body for post/update methods to make the changes and test accordingly. 
    - Use pytests or python test_app.py to run the tests.

API Endpoints:

/signup	        POST	Register a new user
/login	        POST	Log in a user and get a JWT token
/posts	        GET	    Get all blog posts
/posts	        POST	Create a new blog post
/posts/<int:id>	GET	    Get a specific blog post by ID
/posts/<int:id>	PUT	    Update a specific blog post by ID
/posts/<int:id>	DELETE	Delete a specific blog post by ID