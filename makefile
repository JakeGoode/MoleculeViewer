CC = clang
CFLAGS = -Wall -std=c99 -pedantic

all:  mol.o libmol.so filePair molecule_wrap.o _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -lm -o libmol.so

mol.o:  mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

filePair: molecule.i
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I /usr/include/python3.10 -o molecule_wrap.o

_molecule.so: molecule_wrap.o
	$(CC) molecule_wrap.o -shared -lpython3.10 -lmol -L. -L/usr/lib/python3.10/config-3.10-x86_64-linux-gnu -o _molecule.so

clean:  
	rm -f *.o *.so molecule_wrap.c molecule.py