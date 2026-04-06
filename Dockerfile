# Use an official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to install tools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your code files into the container
COPY . .

# Tell the container to run your dashboard
CMD ["python", "app.py"]