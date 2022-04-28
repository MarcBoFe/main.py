import os
a = ['1', '2', '3', '4']
b = ['2', '4']
c = ['2']
d = ['2', '5']
jiji = 2
estaono = True
carpeta = ''


def aver(modo):
    if modo == 1:
        carpeta = 'C:\\hola'
    elif modo == 2:
        capreta = 'C:\\adios'


    if modo == 1:
        carpeta = 'C:\\hola'
    elif modo == 2:
        capreta = 'C:\\adios'




    if modo == 1:
        carpeta = 'C:\\hola'
    elif modo == 2:
        capreta = 'C:\\adios'
    os.write('{}\\archivo.txt'.format(carpeta))


for valor in d:
    if not valor in a:
        estaono = False
        break

if not estaono:
    print('oye un error en las trazas elegidas')
else:
    print('todod ok')
