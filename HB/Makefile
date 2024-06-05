CFLAGS = -Wall

all:    multiplication one_multiplication print_multiplication mult_iterations clean

multiplication:   multiplication.o
        gcc $(CFLAGS) -o multiplication multiplication.o

multiplication.o: multiplication.c
        gcc $(CFLAGS) -c -o multiplication.o multiplication.c

mult_iterations:   mult_iterations.o
        gcc $(CFLAGS) -o mult_iterations mult_iterations.o

mult_iterations.o: mult_iterations.c
        gcc $(CFLAGS) -c -o mult_iterations.o mult_iterations.c

one_multiplication:   one_multiplication.o
        gcc $(CFLAGS) -o one_multiplication one_multiplication.o

one_multiplication.o: one_multiplication.c
        gcc $(CFLAGS) -c -o one_multiplication.o one_multiplication.c

print_multiplication:   print_multiplication.o
        gcc $(CFLAGS) -o print_multiplication print_multiplication.o

print_multiplication.o: print_multiplication.c
        gcc $(CFLAGS) -c -o print_multiplication.o print_multiplication.c

clean:
        rm *.o

remove:
        rm multiplication one_multiplication print_multiplication mult_iterations