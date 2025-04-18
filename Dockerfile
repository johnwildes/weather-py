# Use the official Python image as a base image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port specified in the environment variable
EXPOSE 80

# Define environment variable
ENV DEFAULT_ZIP_CODE=32507

# Set the environment variable for the port
ENV PORT=80

# Command to run the application
CMD ["python", "main.py"]