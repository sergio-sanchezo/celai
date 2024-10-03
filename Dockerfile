# Use a base python image
FROM public.ecr.aws/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

COPY . .

# Install Dependencies
RUN pip install --upgrade pip
RUN pip install -e .

# set port
EXPOSE 3000

# Set execution command for application
CMD ["python", "./main.py"]
