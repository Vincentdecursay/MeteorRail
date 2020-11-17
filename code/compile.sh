#!/bin/bash

# Compile the python file to an linux executable
# https://stackoverflow.com/questions/39913847/is-there-a-way-to-compile-a-python-application-into-static-binary

# Prerequies :
# cython -> pip install cython

cp meteor_stack.py meteor_stack.pyx
cp config.txt ../software/config.txt

cython meteor_stack.pyx --embed

gcc -Os -I /usr/include/python3.5m -o ../software/meteor_stack meteor_stack.c -lpython3.5m -lpthread -lm -lutil -ldl

rm meteor_stack.pyx
rm meteor_stack.c