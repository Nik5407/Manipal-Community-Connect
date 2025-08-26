# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures that Python output is sent straight to terminal (e.g. for Docker logs)
ENV PYTHONUNBUFFERED=1  

# Set work directory
WORKDIR /usr/src/app


# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .
# Expose the port on which your Django app will run
EXPOSE 8000

# # Run the entrypoint script for Django
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Ensure entrypoint.sh has Unix line endings
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix /usr/src/app/entrypoint.sh

# Verify entrypoint.sh exists and is executable
RUN ls -la /usr/src/app/entrypoint.sh

CMD ["/usr/src/app/entrypoint.sh"]