Blog Posting Platform (Backend)
This project is a simple blog posting platform where users can register, log in, and create blog posts. Users can dynamically generate categories and create posts associated with a particular category. Additionally, users can add comments to posts, and others can reply to these comments. All users can view comments and replies, fostering interaction within the platform.

Key Features
User Authentication & Authorization:

Authentication: Only authenticated users can create posts and categories.
Authorization: Users can only delete their own posts. One user cannot delete posts created by another user.
Post Viewing: All users, including non-authenticated users, can view posts without needing to log in.
Dynamic Categories: Users can create custom categories and associate posts with them.

CRUD Operations:

Authenticated users can perform Create, Read, Update, and Delete operations on their posts.
Users must be logged in to create or manage posts and categories.
Comment System: Users can comment on posts, and others can reply to those comments. Comments are visible to all users.

Backend API: This project is backend-only and provides APIs to manage users, posts, categories, and comments.

Project Details
This project primarily focuses on authentication and CRUD operations:

Authenticated Users: Only logged-in users can create and manage posts and categories.
Authorized Actions: Users can only delete or modify their own posts; they cannot modify or delete posts created by others.
View without Login: All posts can be viewed by any user, even without logging in. Authentication is only required for creating posts and categories.
This project was created as a 3-day demo during my internship and was presented in my office.

Setup Instructions
To run this project locally, follow the steps below:

1. Clone the Repository
git clone https://github.com/Aarti-04/Blogging-platform.git
cd Blogging-platform

2. Create a Virtual Environment
It's recommended to run the project in a virtual environment to isolate dependencies. Run the following commands to set it up:

python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
# or
venv\Scripts\activate  # For Windows

3. Install Dependencies
Install the required packages by running:
pip3 install -r requirements.txt

4. Run the Server
After installing the dependencies, you can run the Django development server using:
python3 manage.py runserver

5. Access the API
Once the server is running, you can access the APIs at:

http://127.0.0.1:8000/

Use a tool like Postman to interact with the APIs.

Technologies Used
- Django: A Python web framework for rapid development.
- Django Rest Framework (DRF): For building REST APIs.
- PostgreSQL: The database used for this project is PostgreSQL, a powerful, open-source relational database. Ensure that PostgreSQL is installed and configured on your local machine before running the project.

Key Commands
Install dependencies:

- pip3 install -r requirements.txt

Run the server:

- python3 manage.py runserver

🚧 Note:
There are a few lines of commented code here and there in the project 😅. I will clean it up soon!