import sys
import urllib
import MolDisplay
import molsql
import re
from copy import deepcopy
from io import BytesIO
from io import TextIOWrapper
from http.server import HTTPServer, BaseHTTPRequestHandler

public_files = [ '/index.html', '/sdfUpload.html', '/style.css', '/script.js' ]
db = molsql.Database() # Connect to database
db.create_tables() # Create tables if needed

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        
        if self.path in public_files:
            self.send_response(200)  # OK
            
            if(self.path == '/style.css'):
                self.send_header("Content-type", "text/css")
            
            elif(self.path == '/script.js'):
                self.send_header("Content-type", "text/javascript")
            
            else:
                self.send_header("Content-type", "text/html")

            fp = open(self.path[1:])
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read()
            fp.close()

            # create and send headers
            self.send_header("Content-length", len(page))
            self.end_headers()

            # send the contents
            self.wfile.write(bytes(page, "utf-8"))
        
        elif self.path == "/elementTable.html":
            self.send_response(200) # OK
            self.send_header("Content-type", "text/html")

            # Create html file based on amount of elements in data base
            elem_string = element_top_page

            elements = db.element_name()

            elem_string += '    <label class="labels">Elements:</label>\n'
            elem_string += '    <select id="element_table" name="element_table" size="3">\n'

            for i in elements:
                elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
            
            elem_string += '    </select>\n'

            elem_string += element_bottom_page

            # create and send headers
            self.send_header("Content-length", len(elem_string))
            self.end_headers()
            
            # send the contents
            self.wfile.write(bytes(elem_string, "utf-8"))
        
        elif self.path == "/moleculeList.html":
            self.send_response(200) # OK
            self.send_header("Content-type", "text/html")

            # Create html file based on amount of molecules in data base
            mol_string = molecule_list_top_page

            atom_dict = db.mol_atom()
            bond_dict = db.mol_bond()

            mol_string += '    <label class="labels">Molecules:</label>\n'
            mol_string += '    <select id="molecule_table" name="molecule_table" size="3">\n'

            for i in atom_dict:
                mol_string += '      <option value="%s">Molecule :%s Atoms: %d Bonds: %d</option>\n' % (i, i, atom_dict[i], bond_dict[i])
            
            mol_string += '    </select>\n'

            mol_string += molecule_list_bottom_page

            # create and send headers
            self.send_header("Content-length", len(mol_string))
            self.end_headers()

            # send the contents
            self.wfile.write(bytes(mol_string, "utf-8"))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

    def do_POST(self):
        global mol # Used to access same molecule between statements
        global file # Used to access same sdf file between statements

        if self.path == "/moleculeName.html":
            content_length = int(self.headers['Content-Length'])
            
            #Get binary version on header content
            file_content = self.rfile.read(content_length)
            file = deepcopy(file_content) # Create a copy of rfile contents
            
            r = BytesIO(file_content)
            
            #Use Byte IO to create a TextIOWrapper object to be passed
            file_obj = TextIOWrapper(r)

            #Skip first 4 lines of file
            next(file_obj)
            next(file_obj)
            next(file_obj)
            next(file_obj)

            #Create new molecule
            mol = MolDisplay.Molecule()

            try:
                mol.parse(file_obj) # Test to see if file is correct
            
            except:
                # Display improper sdf file error
                fp = open("upload_f.html")

                # load the specified file
                page = fp.read()
                fp.close()
                
                self.send_response(200) # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(page))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(page, "utf-8"))
            
            else:
                # Display correct sdf file success
                fp = open("upload_s.html")

                # load the specified file
                page = fp.read()
                fp.close()

                self.send_response(200) # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(page))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(page, "utf-8"))
        
        elif self.path == "/moleculeAdd.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            post_vars = urllib.parse.parse_qs(body.decode('utf-8'))

            r = BytesIO(file)
            
            #Use Byte IO to create a TextIOWrapper object to be passed
            file_obj = TextIOWrapper(r)

            #Skip first 4 lines of file
            next(file_obj)
            next(file_obj)
            next(file_obj)
            next(file_obj)
            
            try:
                message = str(post_vars['name'][0]) # Get molecule name
                
                db.add_molecule(message, file_obj) # Test to see if proper molecule name was given
            
            except:
                # load the specified file
                string = molecule_failure
                
                self.send_response(200) # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(string))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(string, "utf-8"))
            
            else:
                # load the specified file and add the molecule to the data base
                string = molecule_success
                
                self.send_response(200) # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(string))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(string, "utf-8"))
        
        elif self.path == "/display.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))

            try:
                molecule = str(postvars['molecule'][0])

                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                #MolDisplay.header += db.radial_gradients()

                mol = db.load_mol(molecule)
                mol.sort()
            
            except:
                self.send_response(204) # No molecule selected 
                self.end_headers()
            
            else:
                # Display selected molecule
                svg_return = MolDisplay.header
                svg_return += db.radial_gradients()
                svg_return += mol.svg()
                svg_return += MolDisplay.footer
                
                self.send_response(200) # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(svg_return))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(svg_return, "utf-8"))
        
        elif self.path == "/updateDisplay.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))

            try:
              # Test to see if proper rotation values were entered
              x = float(postvars['xrot'][0])
              y = float(postvars['yrot'][0])
              z = float(postvars['zrot'][0])

              mol.xform(x, y, z)
              mol.sort()
            
            except:
                # If an error occurred, re-print existing molecule
                svg_return = MolDisplay.header
                svg_return += db.radial_gradients()
                svg_return += mol.svg()
                svg_return += MolDisplay.footer

                self.send_response(204); # Could not rotate molecule
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(svg_return))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(svg_return, "utf-8"))
            
            else:
                # If the rotation succeeded, print the rotated molecule
                svg_return = MolDisplay.header
                svg_return += db.radial_gradients()
                svg_return += mol.svg()
                svg_return += MolDisplay.footer

                self.send_response(200); # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(svg_return))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(svg_return, "utf-8"))

        elif self.path == "/removeElement.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))

            try:
                # Check if data is present
                element = str(postvars['element'][0])

                # Remove element from database
                db.delete_element(element)
            
            except:
                elements = db.element_name()
                
                # Re-send the current element table
                elem_string = '    <label class="labels">Elements:</label>\n'
                elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                for i in elements:
                    elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                
                elem_string += '    </select>\n'

                self.send_response(204); # No element select to remove
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(elem_string))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(elem_string, "utf-8"))

            else:
                elements = db.element_name()
                
                # Update the list html after removal
                elem_string = '    <label class="labels">Elements:</label>\n'
                elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                for i in elements:
                    elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                
                elem_string += '    </select>\n'

                self.send_response(200); # OK
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(elem_string))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(elem_string, "utf-8"))

        elif self.path == "/addElement.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs(body.decode('utf-8'))

            try:
                # Test to check if all fields have been filled out
                number = int(postvars['number'][0])
                code = str(postvars['code'][0])
                name = str(postvars['name'][0])
                radius = int(postvars['radius'][0])
                colour1 = str(postvars['colour1'][0])
                colour2 = str(postvars['colour2'][0])
                colour3 = str(postvars['colour3'][0])
            
            except:
                # If an error occurred, re-print existing html table
                elements = db.element_name()

                elem_string = '    <label class="labels">Elements:</label>\n'
                elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                for i in elements:
                    elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                
                elem_string += '    </select>\n'

                self.send_response(204); # Could not update element table
                
                # create and send headers
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(elem_string))
                self.end_headers()

                # send the contents
                self.wfile.write(bytes(elem_string, "utf-8"))

            else:
                # Check that all colours are valid hex values
                valid_colour1 = self.valid_hex(colour1)
                valid_colour2 = self.valid_hex(colour2)
                valid_colour3 = self.valid_hex(colour3)

                if valid_colour1 and valid_colour2 and valid_colour3 and (len(code) <= 2) and (len(name) <= 32) and ((radius < 1000) and (radius > 0)):
                    try:
                        # Try to enter element into data base
                        db['Elements'] = (number, code, name, colour1, colour2, colour3, radius)
                    
                    except:
                        # If an error occurred, re-print existing html table
                        elements = db.element_name()

                        elem_string = '    <label class="labels">Elements:</label>\n'
                        elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                        for i in elements:
                            elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                        
                        elem_string += '    </select>\n'

                        self.send_response(204); # Could not update element table
                        
                        # create and send headers
                        self.send_header("Content-type", "text/html")
                        self.send_header("Content-length", len(elem_string))
                        self.end_headers()

                        # send the contents
                        self.wfile.write(bytes(elem_string, "utf-8"))
                    
                    else:
                      # If there is no issue with the element, create new list html for all elements
                      elements = db.element_name()

                      elem_string = '    <label class="labels">Elements:</label>\n'
                      elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                      for i in elements:
                          elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                      
                      elem_string += '    </select>\n'

                      self.send_response(200); # OK
                      
                      # create and send headers
                      self.send_header("Content-type", "text/html")
                      self.send_header("Content-length", len(elem_string))
                      self.end_headers()

                      # send the contents
                      self.wfile.write(bytes(elem_string, "utf-8"))
                
                else:
                    # If hex colours are not valid, re-print existing html table
                    elements = db.element_name()

                    elem_string = '    <label class="labels">Elements:</label>\n'
                    elem_string += '    <select id="element_table" name="element_table" size="3">\n'

                    for i in elements:
                        elem_string += '      <option value="%s">%s</option>\n' % (elements[i], elements[i])
                    
                    elem_string += '    </select>\n'

                    self.send_response(204); # Could not update element table
                    
                    # create and send headers
                    self.send_header("Content-type", "text/html")
                    self.send_header("Content-length", len(elem_string))
                    self.end_headers()

                    # send the contents
                    self.wfile.write(bytes(elem_string, "utf-8"))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))
    
    def valid_hex(self, string):
        
        # Regex for hex colour code
        regex = "([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

        # Compile Regex
        list = re.compile(regex)

        if(string == None):
            return False
        
        if(not(len(string) == 3 or len(string) == 6)):
            return False
        
        # Check if string matches hex Regex
        if(re.search(list, string)):
            return True
        else:
            return False

element_top_page = """
<html>
  <head>
    <title> Element List </title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"> </script>
    <script src="script.js" /></script>
    <link rel="stylesheet" type="text/css" href="style.css" />
  </head>
  <body>
    <h1 class="center"> Element List </h1>
    <p>
      <a href="/index.html"> Main Menu </a>
    </p>
    <p>
      <a href="/sdfUpload.html"> File Upload </a>
    </p>
    <p>
      <a href="/moleculeList.html"> Molecule List </a>
    </p>
    <div id ="elements">
"""

element_bottom_page = """
    </div>
    <p>
        <button class="buttons" id="remove"> Remove element </button>
    </p>
    <p>
        <label class="labels" id="e1">Element number:</label>
        <input type="text" id="elemNo"/>
    </p>
    <p>
        <label class="labels" id="e2">Element code:</label>
        <input type="text" id="elemCode"/>
    </p>
    <p>
        <label class="labels" id="e3">Element name:</label>
        <input type="text" id="elemName"/>
    </p>
    <p>
        <label class="labels" id="e4">Colour 1 (Hex 0-F):</label>
        <input type="text" id="colour1"/>
    </p>
    <p>
        <label class="labels" id="e5">Colour 2 (Hex 0-F):</label>
        <input type="text" id="colour2"/>
    </p>
    <p>
        <label class="labels" id="e6">Colour 3 (Hex 0-F):</label>
        <input type="text" id="colour3"/>
    </p>
    <p>
        <label class="labels" id="e7">Radius:</label>
        <input type="text" id="radius"/>
    </p>
    <p>
        <button class="buttons" id="addElem"> Add element </button>
    </p>
  </body>
</html>
"""

molecule_list_top_page = """
<html>
  <head>
    <title> Molecule List </title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"> </script>
    <script src="script.js" /></script>
    <link rel="stylesheet" type="text/css" href="style.css" />
  </head>
  <body>
    <h1 class="center"> Molecule List </h1>
    <p>
      <a href="/index.html"> Main Menu </a>
    </p>
    <p>
      <a href="/sdfUpload.html"> File Upload </a>
    </p>
    <p>
      <a href="/elementTable.html"> Element List </a>
    </p>
    <div id ="molecules">
"""

molecule_list_bottom_page = """
    </div>
    <p>
        <button class="buttons" id="select"> Select Molecule </button>
    </p>
    <div id ="display">
    </div>
    <p id="p1">
      <label class="labels" id="x">X:</label>
      <input type="text" id="xRot"/>
    </p>
    <p id="p2">
      <label class="labels" id="y">Y:</label>
      <input type="text" id="yRot"/>
    </p>
    <p id="p3">
      <label class="labels" id="z">Z:</label>
      <input type="text" id="zRot"/>
    </p>
    <p id="p4">
      <button class="buttons" id="rotate"> Rotate </button>
    </p>
  </body>
</html>
"""

molecule_success = """
    <h1 class="center"> Molecule Added </h1>
    <p class="text">
      Molecule added to database. Return to main menu.
    </p>
    <p>
      <a href="/index.html"> Main Menu </a>
    </p>
"""

molecule_failure = """
    <h1 class="center"> Bad Molecule </h1>
    <p class="text">
      Molecule name already in system or empty name. Return to main menu.
    </p>
    <p>
      <a href="/index.html"> Main Menu </a>
    </p>
"""

httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()
