# Use a minimal Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk2.0-dev \
    libboost-all-dev \
    default-libmysqlclient-dev \
    pkg-config \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    libpq-dev \
    libssl-dev \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# Install Microsoft ODBC Driver 18 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql18 \
    && apt-get clean

# Copy the current directory contents into the container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Default environment variable, can be overridden at runtime
ENV RUN_FILE=app.py

# Use a shell command that runs the file specified in RUN_FILE
CMD ["sh", "-c", "python $RUN_FILE"]
