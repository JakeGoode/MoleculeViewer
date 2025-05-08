#include "mol.h"

void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
    
    strcpy(atom -> element, element);

    atom -> x = *x;
    atom -> y = *y;
    atom -> z = *z;
}

void atomget(atom *atom, char element[3], double *x, double *y, double *z) {

    strcpy(element, atom -> element);

    *x = atom -> x;
    *y = atom -> y;
    *z = atom -> z;
}

void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {

    bond -> a1 = *a1;
    bond -> a2 = *a2;
    bond -> epairs = *epairs;
    bond -> atoms = *atoms;

    compute_coords(bond);
}

void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {

    *a1 = bond -> a1;
    *a2 = bond -> a2;
    *epairs = bond -> epairs;
    *atoms = bond -> atoms;
}

molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {

    molecule *new_mol = malloc(sizeof(molecule));

    //If program cannot allocate memory block for molecule
    if(new_mol == NULL) {
        return NULL;
    }
    else {
        new_mol -> atom_max = atom_max;
        new_mol -> atom_no = 0;
        new_mol -> bond_max = bond_max;
        new_mol -> bond_no = 0;

        new_mol -> atoms = (struct atom *)malloc(atom_max * sizeof(struct atom));
        new_mol -> atom_ptrs = (struct atom **)malloc(atom_max * sizeof(struct atom *));

        new_mol -> bonds = (struct bond *)malloc(bond_max * sizeof(struct bond));
        new_mol -> bond_ptrs = (struct bond **)malloc(bond_max * sizeof(struct bond *));

        return new_mol;
    }
}

molecule *molcopy(molecule *src) {

    molecule *copied_mol = molmalloc(src -> atom_max, src -> bond_max);

    //If program cannot allocate memory block for molecule
    if(copied_mol == NULL) {
        return NULL;
    }
    else {
        bond bond_copy;  //Struct variable used to create bonds with atoms from copy and not from source
        
        //Add atoms from src to copy
        for(int i = 0; i < src -> atom_no; i++) {
            molappend_atom(copied_mol, &(src -> atoms[i]));
        }

        //Add bonds from src to copy
        for(int j = 0; j < src -> bond_no; j++) {
            unsigned short index_a1 = src -> bonds[j].a1;  //Gets atom 1 array's index from source bond
            unsigned short index_a2 = src -> bonds[j].a2;  //Gets atom 2 array's index from source bond

            //Sets copied bond's atom 1 and 2 to copied atoms correct array indexes
            bondset(&bond_copy, &index_a1, &index_a2, &(copied_mol->atoms), &(src -> bonds[j].epairs));
            
            molappend_bond(copied_mol, &bond_copy);
            //molappend_bond(copied_mol, &(src -> bonds[j]));
        }

        return copied_mol;
    }
}

void molfree(molecule *ptr) {
    
    free(ptr -> atom_ptrs);
    free(ptr -> atoms);
    free(ptr -> bond_ptrs);
    free(ptr -> bonds);
    free(ptr);
}

void molappend_atom(molecule *molecule, atom *atom) {

    if(molecule -> atom_no != molecule -> atom_max) {
        molecule -> atoms[molecule -> atom_no] = *atom;
        molecule -> atom_ptrs[molecule -> atom_no] = &(molecule -> atoms[molecule -> atom_no]);
        
        molecule -> atom_no += 1;
    }
    else {
        if(molecule -> atom_max == 0) {
            molecule -> atoms = (struct atom *)realloc(molecule -> atoms, sizeof(struct atom) * 1);
            molecule -> atom_ptrs = (struct atom **)realloc(molecule -> atom_ptrs, sizeof(struct atom *) * 1);

            if(molecule -> atoms == NULL || molecule -> atom_ptrs == NULL) {
                printf("Cannot reserve aditional memory\n");
                exit(0);
            }
            
            molecule -> atoms[0] = *atom;
            molecule -> atom_ptrs[0] = &molecule -> atoms[0];
            
            molecule -> atom_max = 1;
            molecule -> atom_no = 1;
        }
        else {            
            molecule -> atoms = (struct atom *)realloc(molecule -> atoms, sizeof(struct atom) * (molecule -> atom_max * 2));
            molecule -> atom_ptrs = (struct atom **)realloc(molecule -> atom_ptrs, sizeof(struct atom *) * (molecule -> atom_max * 2));

            if(molecule -> atoms == NULL || molecule -> atom_ptrs == NULL) {
                printf("Cannot reserve aditional memory\n");
                exit(0);
            }

            //Loop to re-set atom_ptrs to point to correct atoms in molecule in case memory block is moved during realloc
            for(int i = 0; i < molecule -> atom_no; i++) {
                molecule -> atom_ptrs[i] = &(molecule -> atoms[i]);
            }

            molecule -> atoms[molecule -> atom_no] = *atom;
            molecule -> atom_ptrs[molecule -> atom_no] = &(molecule -> atoms[molecule -> atom_no]);
            
            molecule -> atom_max = molecule -> atom_max * 2;
            molecule -> atom_no += 1;
        }
    }
}

void molappend_bond(molecule *molecule, bond *bond) {
    
    if(molecule -> bond_no != molecule -> bond_max) {
        molecule -> bonds[molecule -> bond_no] = *bond;
        molecule -> bond_ptrs[molecule -> bond_no] = &(molecule -> bonds[molecule -> bond_no]);
        
        molecule -> bond_no += 1;
    }
    else {
        if(molecule -> bond_max == 0) {
            molecule -> bonds = (struct bond *)realloc(molecule -> bonds, sizeof(struct bond) * 1);
            molecule -> bond_ptrs = (struct bond **)realloc(molecule -> bond_ptrs, sizeof(struct bond *) * 1);

            if(molecule -> bonds == NULL || molecule -> bond_ptrs == NULL) {
                printf("Cannot reserve aditional memory\n");
                exit(0);
            }
            
            molecule -> bonds[0] = *bond;
            molecule -> bond_ptrs[0] = &molecule -> bonds[0];
            
            molecule -> bond_max = 1;
            molecule -> bond_no = 1;
        }
        else {            
            molecule -> bonds = (struct bond *)realloc(molecule -> bonds, sizeof(struct bond) * (molecule -> bond_max * 2));
            molecule -> bond_ptrs = (struct bond **)realloc(molecule -> bond_ptrs, sizeof(struct bond *) * (molecule -> bond_max * 2));

            if(molecule -> bonds == NULL || molecule -> bond_ptrs == NULL) {
                printf("Cannot reserve aditional memory\n");
                exit(0);
            }

            //Loop to re-set bond_ptrs to point to correct bonds in molecule in case memory block is moved during realloc
            for(int i = 0; i < molecule -> bond_no; i++) {
                molecule -> bond_ptrs[i] = &(molecule -> bonds[i]);
            }

            molecule -> bonds[molecule -> bond_no] = *bond;
            molecule -> bond_ptrs[molecule -> bond_no] = &(molecule -> bonds[molecule -> bond_no]);
            
            molecule -> bond_max = molecule -> bond_max * 2;
            molecule -> bond_no += 1;
        }
    }
}

void molsort(molecule *molecule) {

    //Sort atom_ptrs based on ascending z-values from atoms array
    qsort(molecule -> atom_ptrs, molecule -> atom_no, sizeof(molecule -> atom_ptrs[0]), atomCompare);

    //Sort bond_ptrs based on ascending z-values from bonds array
    qsort(molecule -> bond_ptrs, molecule -> bond_no, sizeof(molecule -> bond_ptrs[0]), bond_comp);
}

void xrotation(xform_matrix xform_matrix, unsigned short deg) {

    //Sets matrix to x-axis rotation per information from https://en.wikipedia.org/wiki/Rotation_matrix

    double radian = deg * (M_PI/180.0);

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = xform_matrix[0][2] = xform_matrix[1][0] = xform_matrix[2][0] = 0;

    xform_matrix[1][1] = cos(radian);
    xform_matrix[1][2] = -1 * (sin(radian));
    xform_matrix[2][1] = sin(radian);
    xform_matrix[2][2] = cos(radian);
}

void yrotation(xform_matrix xform_matrix, unsigned short deg) {
    
    //Sets matrix to y-axis rotation per information from https://en.wikipedia.org/wiki/Rotation_matrix
    
    double radian = deg * (M_PI/180.0);

    xform_matrix[1][1] = 1;
    xform_matrix[0][1] = xform_matrix[1][0] = xform_matrix[1][2] = xform_matrix[2][1] = 0;

    xform_matrix[0][0] = cos(radian);
    xform_matrix[0][2] = sin(radian);
    xform_matrix[2][0] = -1 * (sin(radian));
    xform_matrix[2][2] = cos(radian);
}

void zrotation(xform_matrix xform_matrix, unsigned short deg) {

    //Sets matrix to z-axis rotation per information from https://en.wikipedia.org/wiki/Rotation_matrix
    
    double radian = deg * (M_PI/180.0);

    xform_matrix[2][2] = 1;
    xform_matrix[0][2] = xform_matrix[1][2] = xform_matrix[2][0] = xform_matrix[2][1] = 0;

    xform_matrix[0][0] = cos(radian);
    xform_matrix[0][1] = -1 * (sin(radian));
    xform_matrix[1][0] = sin(radian);
    xform_matrix[1][1] = cos(radian);
}

void mol_xform(molecule *molecule, xform_matrix matrix) {

    //3x1 * 3x3 matrix multiplication to create new x,y,z values for each atom in array

    for(int i = 0; i < molecule -> atom_no; i++) {
        double old_X = molecule -> atoms[i].x;
        double old_Y = molecule -> atoms[i].y;
        double old_Z = molecule -> atoms[i].z;
        
        molecule -> atoms[i].x = (old_X * matrix[0][0]) + (old_Y * matrix[0][1]) + (old_Z * matrix[0][2]);
        molecule -> atoms[i].y = (old_X * matrix[1][0]) + (old_Y * matrix[1][1]) + (old_Z * matrix[1][2]);
        molecule -> atoms[i].z = (old_X * matrix[2][0]) + (old_Y * matrix[2][1]) + (old_Z * matrix[2][2]);
    }

    for(int j = 0; j < molecule -> bond_no; j++) {

        compute_coords(&(molecule -> bonds[j]));
    }
}

int atomCompare(const void *p1, const void *p2) {
    
    const atom *a1 = *(atom **)p1;
    const atom *a2 = *(atom **)p2;

    if(a1 -> z < a2 -> z) {
        return -1;
    }
    else if(a1 -> z > a2 -> z) {
        return 1;
    }
    else {
        return 0;
    }
}

int bond_comp(const void *a, const void *b) {
    
    const bond *b1 = *(bond **)a;
    const bond *b2 = *(bond **)b;

    if(b1 -> z < b2 -> z) {
        return -1;
    }
    else if(b1 -> z > b2 -> z) {
        return 1;
    }
    else {
        return 0;
    }
}

void compute_coords(bond *bond) {
    
    double xLen = 0;
    double yLen = 0;
    
    bond -> x1 = bond -> atoms[bond -> a1].x;
    bond -> y1 = bond -> atoms[bond -> a1].y;

    bond -> x2 = bond -> atoms[bond -> a2].x;
    bond -> y2 = bond -> atoms[bond -> a2].y;

    bond -> z = (bond -> atoms[bond -> a1].z + bond -> atoms[bond -> a2].z) / 2;

    xLen = (bond -> atoms[bond -> a2].x - bond -> atoms[bond -> a1].x) * (bond -> atoms[bond -> a2].x - bond -> atoms[bond -> a1].x);
    yLen = (bond -> atoms[bond -> a2].y - bond -> atoms[bond -> a1].y) * (bond -> atoms[bond -> a2].y - bond -> atoms[bond -> a1].y);

    bond -> len = sqrt(xLen + yLen);

    bond -> dx = (bond -> atoms[bond -> a2].x - bond -> atoms[bond -> a1].x) / bond -> len;
    bond -> dy = (bond -> atoms[bond -> a2].y - bond -> atoms[bond -> a1].y) / bond -> len;
}
