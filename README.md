# Molecule-Viewer
Full-Stack application that manipulates .sdf files to generate molecules in svg format

# Project Structure 
- ```mol.c ``` Library written in C that manipulates molecules, atoms and bonds 
- ```mol.h ``` Header file that contains all of the functions
- ```MolDisplay.py``` Python module that generates SVGS for molecules, atoms and bonds
- ```molsql.py``` Python module that generates a SQLite database to perform various database operations
- ```server.py``` Custom python server that interacts with the client
- ```molecule.i``` file used to interact with swig toolkit to compile scripted languages together
- ```script.js``` JavaScript to implement event listeners and HTTP requests via AJAX to interact with server

# Requirements

1. Download python3.1 on your local machine https://www.python.org/downloads/
2. Download Swig3.0 on your local machine https://open-box.readthedocs.io/en/latest/installation/install_swig.html

# How to run

1. Clone the repo locally
2. Change the python installation pathways that are native to your local machine in ```makefile``` 
3. Run ```make``` in the project directory, this will generate the necessary dependencies, including the object files
4. Run ```export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.``` to locate the shared libraries in the current directory
5. Run ```python3 server.py 8000``` to start the server locally
6. Navigate to ```localhost:8000```