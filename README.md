# Advanced Web Development Group Project

### Students:

Raj Shukla (Student ID: 100784045)

### Description:

The following project is an API that uses SQLAlchemy to store user data with JWT for authorization and security of users. It uses the Model View Controller (MVC) architecture format to organize file systems. 

### Setup

#### Step 0: Enter Virtual Environment
Using either of the following commands for windows or mac from the terminal you can enter the virtual enviroment. It is recommended you do this before beginning to do anything.
For macOS/Linux
```
source venv/bin/activate
```
For Windows
```
venv\Scripts\activate
```

#### Step 1: Installing Docker

Windows:
1. Go to https://www.docker.com/get-started and download Docker Desktop.
2. Follow the installation prompts.
3. Open Docker Desktop and ensure it runs without errors.
   
Linux:
1. Follow the installation guide for your Linux distribution at
https://docs.docker.com/engine/install/.
2. Start Docker with: sudo systemctl start docker
3. Verify installation with: docker --version
   
macOS:
1. Download Docker Desktop from https://www.docker.com/get-started.
2. Install and run Docker Desktop.
3. Confirm installation by running: docker --version

#### Step 2: Pull the repository

Use the following command to pull the repository with the terminal. NOTE: make sure you are switched into the right repository.
```
git pull https://github.com/Raj-Shukla2002/AdvWebDev-project.git
```

#### Step 3: Build Docker Image
Use the following command to build the docker image.
```
docker build -t group-project-4045 .
```
#### Step 4: Verify Docker Image was made
Use the following command to verify that the Docker Image was made successfully
```
docker images
```
#### Step 5: Run the container
Use the following command to run the container
```
docker run -d -p 5000:5000 group-project-4045
```
#### Step 6: Verify Container is running
Using the following command you can see if the docker container is running
```
docker ps
```
