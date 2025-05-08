import MolDisplay
import sqlite3
import os

radialGradientSVG = """
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
    <stop offset="0%%" stop-color="#%s"/>
    <stop offset="50%%" stop-color="#%s"/>
    <stop offset="100%%" stop-color="#%s"/>
  </radialGradient>"""

class Database:

    def __init__(self, reset=False):
        #If reset=True, find and delete old table
        if reset:
            if os.path.exists("molecules.db"):
                os.remove("molecules.db")
        
        self.conn = sqlite3.connect("molecules.db")


    def create_tables(self):
        #This method checks to see if any table exists and if not, create a new one

        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'Elements';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE Elements (
                                  ELEMENT_NO    INTEGER NOT NULL UNIQUE,
                                  ELEMENT_CODE  VARCHAR (3) NOT NULL UNIQUE,
                                  ELEMENT_NAME  VARCHAR (32) NOT NULL UNIQUE,
                                  COLOUR1       CHAR (6) NOT NULL,
                                  COLOUR2       CHAR (6) NOT NULL,
                                  COLOUR3       CHAR (6) NOT NULL,
                                  RADIUS        DECIMAL (3) NOT NULL,
                                  PRIMARY KEY   (ELEMENT_CODE));""")
        
        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'Atoms';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE Atoms (
                                  ATOM_ID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  ELEMENT_CODE  VARCHAR (3) NOT NULL,
                                  X             DECIMAL (7,4) NOT NULL,
                                  Y             DECIMAL (7,4) NOT NULL,
                                  Z             DECIMAL (7,4) NOT NULL,
                                  FOREIGN KEY   (ELEMENT_CODE) REFERENCES Elements);""")
        
        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'Bonds';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE Bonds (
                                  BOND_ID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  A1            INTEGER NOT NULL,
                                  A2            INTEGER NOT NULL,
                                  EPAIRS        INTEGER NOT NULL);""")
            
        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'Molecules';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE Molecules (
                                  MOLECULE_ID   INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                  NAME          TEXT NOT NULL UNIQUE);""")
        
        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'MoleculeAtom';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE MoleculeAtom (
                                  MOLECULE_ID   INTEGER NOT NULL,
                                  ATOM_ID       INTEGER NOT NULL,
                                  PRIMARY KEY   (MOLECULE_ID, ATOM_ID),
                                  FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                  FOREIGN KEY (ATOM_ID) REFERENCES Atoms);""")
        
        data = self.conn.execute("""SELECT name FROM sqlite_master
                                     WHERE
                                     type = 'table' AND name = 'MoleculeBond';""")
        
        table = data.fetchall()
        
        #If table does not exist, create one
        if table == []:
            self.conn.execute("""CREATE TABLE MoleculeBond (
                                  MOLECULE_ID   INTEGER NOT NULL,
                                  BOND_ID       INTEGER NOT NULL,
                                  PRIMARY KEY   (MOLECULE_ID, BOND_ID),
                                  FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                                  FOREIGN KEY (BOND_ID) REFERENCES Bonds);""")

    
    def __setitem__(self, table, values):
        #values argument is listed as a tuple object
        if table == "Elements":
            self.conn.execute("""INSERT
                                 INTO Elements (ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS)
                                 VALUES        (?, ?, ?, ?, ?, ?, ?); """, (values[0], values[1], values[2], values[3], values[4], values[5], values[6]))
        elif table == "Atoms":
            self.conn.execute("""INSERT
                                 INTO Atoms (ELEMENT_CODE, X, Y, Z)
                                 VALUES     (?, ?, ?, ?); """, (values[0], values[1], values[2], values[3]))
        elif table == "Bonds":
            self.conn.execute("""INSERT
                                 INTO Bonds (A1, A2, EPAIRS)
                                 VALUES     (?, ?, ?); """, (values[0], values[1], values[2]))
        elif table == "Molecules":
            self.conn.execute("""INSERT
                                 INTO Molecules (NAME)
                                 VALUES     (?); """, (values[0],))
        elif table == "MoleculeAtom":
            self.conn.execute("""INSERT
                                 INTO MoleculeAtom (MOLECULE_ID, ATOM_ID)
                                 VALUES     (?, ?); """, (values[0], values[1]))
        elif table == "MoleculeBond":
            self.conn.execute("""INSERT
                                 INTO MoleculeBond (MOLECULE_ID, BOND_ID)
                                 VALUES     (?, ?); """, (values[0], values[1]))
            
        self.conn.commit() #Save changes to table

    def add_atom(self, molname, atom):
        #Add to Atoms table
        self.__setitem__("Atoms", (atom.element, atom.x, atom.y, atom.z))

        data = self.conn.execute("""SELECT Molecules.MOLECULE_ID
                                    FROM Molecules
                                    WHERE Molecules.NAME = ?;""", (molname,))
        
        molID = data.fetchone()
        
        data = self.conn.execute("""SELECT last_insert_rowid();""")
        
        atomID = data.fetchone()

        #Add MOLECULE_ID and ATOM_ID to MoleculeAtom table
        self.__setitem__("MoleculeAtom", (molID[0], atomID[0]))

    def add_bond(self, molname, bond):
        #Add to Bond table
        self.__setitem__("Bonds", (bond.a1, bond.a2, bond.epairs))

        data = self.conn.execute("""SELECT Molecules.MOLECULE_ID
                                    FROM Molecules
                                    WHERE Molecules.NAME = ?;""", (molname,))
        
        molID = data.fetchone()

        data = self.conn.execute("""SELECT last_insert_rowid();""")
        
        bondID = data.fetchone()

        #Add MOLECULE_ID and BOND_ID to MoleculeBond table
        self.__setitem__("MoleculeBond", (molID[0], bondID[0]))

    def add_molecule(self, name, fp):
        #Create new molecule and parse file to update molecule
        mol = MolDisplay.Molecule()

        mol.parse(fp)

        #Add molecule to Molecule table
        self.__setitem__("Molecules", (name,))

        #Loop through molecule and add all atoms to Atoms table
        for i in range(0, mol.atom_no):
            atom = mol.get_atom(i)
            self.add_atom(name, atom)

        #Loop through molecule and add all bonds to Bonds table
        for i in range(0, mol.bond_no):
            bond = mol.get_bond(i)
            self.add_bond(name, bond)

    def load_mol(self, name):
        #Create new molecule
        mol = MolDisplay.Molecule()

        #Find all the atoms that belong to the molecule
        data = self.conn.execute("""SELECT Atoms.ELEMENT_CODE,
                                    Atoms.X,
                                    Atoms.Y,
                                    Atoms.Z
                                    FROM Molecules, MoleculeAtom, Atoms
                                    WHERE (Molecules.NAME = ?
                                    AND Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                                    AND MoleculeAtom.ATOM_ID = Atoms.ATOM_ID);""", (name,))
        
        list = data.fetchall()

        #Loop to add all atoms to molecule object
        for i in list:
            mol.append_atom(str(i[0]), float(i[1]), float(i[2]), float(i[3]))

        #Find all the bonds that belong to the molecule
        data = self.conn.execute("""SELECT Bonds.A1,
                                    Bonds.A2,
                                    Bonds.EPAIRS
                                    FROM Molecules, MoleculeBond, Bonds
                                    WHERE (Molecules.NAME = ?
                                    AND Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                                    AND MoleculeBond.BOND_ID = Bonds.BOND_ID);""", (name,))
        
        list = data.fetchall()

        #Loop to add all bonds to molecule object
        for j in list:
            mol.append_bond(int(j[0]), int(j[1]), int(j[2]))

        return mol

    def radius(self):
        data = self.conn.execute("""SELECT Elements.ELEMENT_CODE,
                                    Elements.RADIUS
                                    FROM Elements;""")
        
        list = data.fetchall()
        
        radius_dict = dict()

        #Loop to create radius dictionary from data provided by Elements table
        for i in list:
            radius_dict[str(i[0])] = int(i[1])
        
        return radius_dict

    def element_name(self):
        data = self.conn.execute("""SELECT Elements.ELEMENT_CODE,
                                    Elements.ELEMENT_NAME
                                    FROM Elements;""")
        
        list = data.fetchall()
        
        name_dict = dict()

        #Loop to create element_name dictionary from data provided by Elements table
        for i in list:
            name_dict[str(i[0])] = str(i[1])
        
        return name_dict

    def radial_gradients(self):
        data = self.conn.execute("""SELECT Elements.ELEMENT_NAME, 
                                    Elements.COLOUR1, 
                                    Elements.COLOUR2, 
                                    Elements.COLOUR3
                                    FROM Elements;""")
        
        list = data.fetchall()
        
        string = ''
        #Add in default colouring
        string += radialGradientSVG % ('Default', 'FFFFFF', '050505', '020202')

        #Loop to create gradients based on data provided by Elements table
        for i in list:         
            string += radialGradientSVG % (str(i[0]), str(i[1]), str(i[2]), str(i[3]))
        
        return string
    
    def delete_element(self, name):
        #Select element from table to delete
        self.conn.execute("""DELETE FROM Elements
                             WHERE (Elements.ELEMENT_NAME = ?);""", (name,))
        
        self.conn.commit() #Save changes to table

    def mol_atom(self):
        data = self.conn.execute("""SELECT Molecules.NAME
                                    FROM Molecules;""")
        
        molecules = data.fetchall()
        
        atom_dict = dict()

        #Loop to create mol_atom dictionary from data provided by Atoms table
        for i in range(len(molecules)):

            #Find all the atoms that belong to the molecule
            data = self.conn.execute("""SELECT Atoms.ELEMENT_CODE
                                    FROM Molecules, MoleculeAtom, Atoms
                                    WHERE (Molecules.NAME = ?
                                    AND Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                                    AND MoleculeAtom.ATOM_ID = Atoms.ATOM_ID);""", (molecules[i][0],))
        
            atoms = data.fetchall()

            atom_len = len(atoms)

            atom_dict[str(molecules[i][0])] = int(atom_len)
        
        return atom_dict
    
    def mol_bond(self):
        data = self.conn.execute("""SELECT Molecules.NAME
                                    FROM Molecules;""")
        
        molecules = data.fetchall()
        
        bond_dict = dict()

        #Loop to create mol_bond dictionary from data provided by Bonds table
        for i in range(len(molecules)):

            #Find all the bonds that belong to the molecule
            data = self.conn.execute("""SELECT Bonds.EPAIRS
                                        FROM Molecules, MoleculeBond, Bonds
                                        WHERE (Molecules.NAME = ?
                                        AND Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                                        AND MoleculeBond.BOND_ID = Bonds.BOND_ID);""", (molecules[i][0],))
            
            bonds = data.fetchall()

            bond_len = len(bonds)

            bond_dict[str(molecules[i][0])] = int(bond_len)
        
        return bond_dict

# if __name__ == "__main__":
#     db = Database(reset=True)
#     db.create_tables()

#     db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 )
#     db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 )
#     db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 )
#     db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 )

#     fp = open( 'water-3D-structure-CT1000292221.sdf' )
#     db.add_molecule( 'Water', fp )

#     fp = open( 'caffeine-3D-structure-CT1001987571.sdf' )
#     db.add_molecule( 'Caffeine', fp )

#     fp = open( 'CID_31260.sdf' )
#     db.add_molecule( 'Isopentanol', fp )

#     # display tables
#     print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() )
#     print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() )
#     print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() )
#     print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() )
#     print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() )
#     print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() )

# if __name__ == "__main__":
#     db = Database(reset=False) # or use default

#     MolDisplay.radius = db.radius()
#     MolDisplay.element_name = db.element_name()
#     MolDisplay.header += db.radial_gradients()

#     for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
#         mol = db.load_mol( molecule )
#         mol.sort()
#         fp = open( molecule + ".svg", "w" )
#         fp.write( mol.svg() )
#         fp.close()
