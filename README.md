# GoalHub
#### Overall Description:
GoalHub is a web-based application using Flask with JavaScript, Python, and SQL. The goal of GoalHub is to help users manage and track their personal goals. With features like goal creation, progress tracking, and motivational content, GoalHub provides a simple and efficient way for users to stay on track and achieve their objectives.
#### Features:
- **Goalhub's Homepage (index.html)**: The homepage of Goalhub gives a brief amount of username about the website and its goals. Once the user is logged in however, it changes briefly and instead gives information on how to navigate the website.

- **Registration (register.html)**: In order to use the features of the app, the user must need to create an account with GoalHub. When an account is created, their username, password, and the time that they created their account are added to a goalhub database table named 'users'. The user can be uniquely identified using their user ID, which is created when the entry occurs in the database. Usernames are uniquely, and passwords are hashed to increase overall security of GoalHub.

- **Login (login.html)**: Once the user has registered with GoalHub, they can login using the username and password that they created. Once the user is logged in, they have access to all features that GoalHub provides.

- **Change Password (changePassword.html)**: Once the user has logged in, if they feel the need to, they can change their password. They must provide their original password (for security) and then their new one. The old password hash in the database will be replaced with the hash of the new password, thereby changing the user's password. Whenever the user wants to login again, they must use that new password.

- **Create Goals (create.html)**: The user can create goals by setting a priority of the goal, writing the goal, and then date you want the goal to be completed by. The form the user needs to fill out is very easy to understand. Once the user submits the form, the goal will be added to a table in the goalhub database named 'goals'. This table consists of the user ID that the goal is for, the priority, the goal, the goal date, and the timestamp it was submitted. The goal can be uniquely identified using its goal ID.

- **Track Progress (progress.html)**: Once the user creates a goal, they will be able to track its progress. The user can see all of their goals, including its priority, goal completion date, and the date the goal was submitted. The format of the table is very easy to read and understand in order to improve the user experience. The user can also sort this table by its priority, completion date, or submitted date in either ascending or descending order to fit their needs perfectly.

- **Remove Goal (remove.html)**: If the user wants to remove a goal (hopefully because they completed it), they can remove it by simply selecting the goal they want to remove and removing it.

- **Motivation Video (motivation.html)**: If the user needs some motivation to pursue their goals, a random motivation video will play in order to try to motivate users to complete their goals and missions.

All of the features mentioned above are located on their own HTML pages. All of these pages can be accessed using the navigation bar on top of the page. All of the features that require the user to login are hidden whenever the user isn't logged in, encouraging the user to make an account.

#### Layout:
The *layout.html* file defines the overall layout of the web application and uses Jinja for the frontend. It includes the navigation bar and footer. The main content area of the layout is defined by a placeholder block, which allows other HTML pages to insert their specific content. All other HTML files in the application use layout.html to maintain a consistent layout.

#### GoalHub's Backend:
GoalHub's backend is built using Flask and sqlite3. The backend handles user requests, manages database operations, and serves appropriate content to the frontend.
- **app.py**: Contains routes allow users to interact with the application via their browser. Each route corresponds to a specific page or action within the app.
- **helpers.py**: Contains helper functions for the main app. The login_required function makes sure that users cannot access specific routes that require authentication unless they are logged in. The todate function converts a YYYY-MM-DD date to a readable text format.
- **goalhub.db**: The database that contains all information about GoalHub in its two tables, *users* and *goals*. Accessing this database and changing its contents is all done in specific routes in the app.py file.

When a user visits the site, Flask routes determine which HTML page should be displayed. If the user interacts with the site (like using the navigation bar or submitting a form), Flask handles the requests, interacts with the SQLite3 database, and returns the necessary response. The helpers.py functions ensure security (login authentication) and data consistency (date formatting).

#### How to Use (Flask on Linux):
GoalHub is very easy to use once python is installed on your machine. Firstly, if you want, create a virtual environment using *python3 -m venv env* to create an environment named "env" (can be named whatever you want). Then, to activate the environment, do the command *source env/bin/activate*. Then, to install all of the app's requirements, run *pip install -r requirements.txt*. After this, use *flask run* and click the link to open up the website.
