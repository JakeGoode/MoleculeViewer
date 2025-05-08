import molecule

header = """<svg version="1.1" width="1000" height="1000"
                   xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""

offsetx = 500
offsety = 500

class Atom:

    def __init__(self, c_atom):
        self.c_atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return '%s %.2f %.2f %.2f' % (self.c_atom.element, self.c_atom.x, self.c_atom.y, self.c_atom.z)

    def svg(self):
        #print(self.z)
        cx = (self.c_atom.x * 100) + offsetx #Centre of atom x-coordinate
        cy = (self.c_atom.y * 100) + offsety #Centre of atom y-coordinate
        
        if self.c_atom.element in element_name:
            return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)" onclick="alert( \'Atom: %s\' )"/>\n' % (cx, cy, radius[self.c_atom.element], element_name[self.c_atom.element], element_name[self.c_atom.element])
        else:
            return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)" onclick="alert( \'Atom: %s\' )"/>\n' % (cx, cy, 20, 'Default', self.c_atom.element) #Default element

class Bond:

    def __init__(self, c_bond):
        self.c_bond = c_bond
        self.z = c_bond.z
    
    def __str__(self):
        return '%d %d %d %.2f %.2f %.2f %.2f %.2f %.2f %.2f' % (self.c_bond.a1, self.c_bond.a2, 
                                                                self.c_bond.epairs, self.c_bond.x1, 
                                                                self.c_bond.y1, self.c_bond.x2, self.c_bond.y2, 
                                                                self.c_bond.len, self.c_bond.dx, self.c_bond.dy)

    def svg(self):
        #print(self.z)
        px = -(self.c_bond.dy)
        py = self.c_bond.dx
        
        #X and Y coordinates between two atoms in a counter-clockwise motion
        b1p1x = ((self.c_bond.x1 * 100) + offsetx) - px * 10.0 #Atom 1, top x position
        b1p1y = ((self.c_bond.y1 * 100) + offsety) - py * 10.0 #Atom 1, top y position
        b1p2x = ((self.c_bond.x1 * 100) + offsetx) + px * 10.0 #Atom 1, bottom x position
        b1p2y = ((self.c_bond.y1 * 100) + offsety) + py * 10.0 #Atom 1, bottom y position
        b2p2x = ((self.c_bond.x2 * 100) + offsetx) + px * 10.0 #Atom 2, bottom x position
        b2p2y = ((self.c_bond.y2 * 100) + offsety) + py * 10.0 #Atom 2, bottom y position
        b2p1x = ((self.c_bond.x2 * 100) + offsetx) - px * 10.0 #Atom 2, top x position
        b2p1y = ((self.c_bond.y2 * 100) + offsety) - py * 10.0 #Atom 2, top y position

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green" onclick="alert( \'Bond between atoms %d and %d\' )"/>\n' % (b1p1x, b1p1y, b1p2x, b1p2y, b2p2x, b2p2y, b2p1x, b2p1y, int(self.c_bond.a1 + 1), int(self.c_bond.a2 + 1))

class Molecule(molecule.molecule):
    
    def __str__(self):
        for i in range(0, self.atom_no):
            atom = self.get_atom(i)
            print( atom.element, atom.x, atom.y, atom.z )

        for i in range(0, self.bond_no):
            bond = self.get_bond(i)
            print( bond.a1, bond.a2, bond.epairs, bond.x1, bond.y1, bond.x2, bond.y2, bond.len, bond.dx, bond.dy )

    def svg(self):
        i = 0
        j = 0
        #svg_string = header
        svg_string = ""

        #self.sort() #Sort the molecule based on z-value

        #Merging atoms and bonds in molecule based on increasing z-value
        c_atom = self.get_atom(i)
        c_bond = self.get_bond(j)
        while i < self.atom_no and j < self.bond_no:
            if c_atom.z < c_bond.z:
                svg_string += Atom(c_atom).svg()
                i += 1
                c_atom = self.get_atom(i)
            else:
                svg_string += Bond(c_bond).svg()
                j+= 1
                c_bond = self.get_bond(j)
        
        #Add any leftover atoms in molecule
        while i < self.atom_no:
            svg_string += Atom(c_atom).svg()
            i += 1
            c_atom = self.get_atom(i)
        
        #Add any leftover bonds in molecule
        while j < self.bond_no:
            svg_string += Bond(c_bond).svg()
            j+= 1
            c_bond = self.get_bond(j)
        
        #svg_string += footer

        #Create svg file
        #svg_file = open("molecule.svg", "w")
        #svg_file.write(svg_string)
        #svg_file.close() #Close svg file

        return svg_string

    def parse(self, file_obj):
        #Skip first 3 lines of file
        for file_line in range(3):
            file_line = file_obj.readline()

        #Read line and split into different fields to get number of atoms and bonds
        file_line = file_obj.readline()
        line = file_line.split()
        count = 4 #Set count after first 4 lines read

        atoms = int(line[0])
        bonds = int(line[1])

        #Loop to get atoms from file
        for line in range(count, count + atoms):
            #Read line and split into different fields to get corrent atom values
            file_line = file_obj.readline()
            line = file_line.split()
            self.append_atom(str(line[3]), float(line[0]), float(line[1]), float(line[2]))

        #Add number of atoms to count
        count += atoms

        #Loop to get bonds from file
        for line in range(count, count + bonds):
            #Read line and split into different fields to get corrent bond values
            file_line = file_obj.readline()
            line = file_line.split()
            self.append_bond(int(line[0]) - 1, int(line[1]) - 1, int(line[2]))
