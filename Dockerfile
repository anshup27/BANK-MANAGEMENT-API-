# Use the official Python 3.8 slim image as the base image
FROM python:3.8-slim

# Set the working directory within the container
WORKDIR /api-flask

# Copy the necessary files and directories into the container

COPY static/ /api-flask/static/
COPY util/ /api-flask/util/
COPY .env /api-flask/.env
COPY .gitignore /api-flask/.gitignore
COPY application.py /api-flask/application.py
COPY auth.py /api-flask/auth.py

COPY student_routes.py /api-flask/student_routes.py
COPY student_model.py /api-flask/student_model.py
COPY students.db /api-flask/students.db
COPY requirements.txt /api-flask/requirements.txt 
COPY test_students.py /api-flask/test_students.py

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "application:app", "-b", "0.0.0.0:5000", "-w", "4"]
