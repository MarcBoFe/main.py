import os
from datetime import datetime
import os.path
from os import remove


# Def: Crea una carpeta con la hora y fecha actual en el directorio dado.
# Var ent: parent_dir: Poner dirección. Ejemplo:"C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico"
# Var sal: crear carpeta.

def crear_carpeta_fecha(parent_dir, impresora):
    # Nombre del directorio.Obtener fecha y hora
    nom_directory = datetime.today().strftime('%Y_%m_%d_%H%M_') + impresora
    # ¿??¿
    path = os.path.join(parent_dir, nom_directory)
    # Generamos el directorio.
    try:
        os.mkdir(path)
    except OSError:
        print("La creación del directorio %s falló," % path)
    else:
        print("Se ha creado el directorio con fecha y hora actual donde vamos a guardar las trazas descargadas. Nombre del directorio: %s " % path)

    return nom_directory


# Def: Crear una carpeta con el nombre y directorio dados.
# Var ent: nom_directory: nombre del directorio. parent_dir:direccion del directorio.
# Var sal: crear carpeta.

def crear_carpeta(nom_directory, parent_dir):
    path = os.path.join(parent_dir, nom_directory)

    try:
        os.mkdir(path)
    except OSError:
        print("La creación del directorio %s falló," % path)
    else:
        print("Se ha creado el directorio: %s " % path)


# Dercarga el archivo seleccionado.
# Var ent: dir_carp_local: carpeta donde se guarda el archivo. archivo: nombre del archivo a descargar. dir_carp_remoto:dirección de la carpeta remota.
# Var sal: Descargar el archivo.

def descargar_un_archivo(dir_carp_local, archivo, dir_carp_remoto):
    remotefileth = "%(ruta)s/%(nombre)s" % dict(ruta=dir_carp_remoto, nombre=archivo)  # '/tmp/HWQY/ScanAxis/total.txt'
    localfilepath = "%(ruta)s/%(nombre)s" % dict(ruta=dir_carp_local,
                                                 nombre=archivo)  # 'C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico/total.txt'

    ftp_client = ssh.open_sftp()
    ftp_client.get(remotefileth, localfilepath)


# Descarga todos los archivos de una carpeta y ponerlos en una carpeta en local.
# Var.ent: dir_carp_remot: dirección de la carpeta remoto.Ejemplo:'/tmp/HWQY/ScanAxis/Traces/2022-01-03' dir_carp_local:dirección carpeta local. Ejemplo:'C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico'
# Var.sali: Genera los archivos en la carpeta.

def descargar_archivos_carpeta(dir_carp_local, dir_carp_remot, ssh):
    sftp_client = ssh.open_sftp()

    archivos = sftp_client.listdir(dir_carp_remot)

    for archivo in archivos:
        remotefileth = "%(ruta)s/%(nombre)s" % dict(ruta=dir_carp_remot, nombre=archivo)
        localfilepath = "%(ruta)s/%(nombre)s" % dict(ruta=dir_carp_local, nombre=archivo)

        sftp_client.get(remotefileth, localfilepath)


# Saca el numero del ciclo del nombre de la traza. Ademas, elimina de la carpeta el archivo time.log
# Var_ent: directorio de las trazas a analizar. EJemplo: 'C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico/2022_01_26_1548'
# Var_sal: total_nom lista donde tenemos todos los valores de las trazas.
def obte_nom_traz_filt(directorio):

    # Eliminamos time.log
    try:
        elim_time = os.path.join(directorio, 'time.log')
        remove(elim_time)
        print('time.log borrado con exito')

    except FileNotFoundError:
        print('time.log no existe')

    # Obtenemos la lista de todos los nombres de los archivos.
    nom_trazas = os.listdir(directorio)

    # Declaramos variable.
    total_nom = []

    # Leemos todos los nombres de los archivos
    for nom_traza in nom_trazas:

        ini_nom = []
        ini = 0

        # Leemos cada una de las letras del nombre del archivo.
        for pos in nom_traza:

            if pos == '_':
                ini = 1
                continue

            if pos == '.':
                ini = 0
                conv_ini_nom = ''.join(map(str, ini_nom))
                total_nom.append(conv_ini_nom)
                ini_nom = 0

            if ini == 1:
                ini_nom.append(pos)

    return total_nom


def conv_nom_impre(lista_impresoras):
    cont = 0
    nom_carpeta = []
    lista_conv_impre = []
    nom_carpeta.clear()

    for impre in lista_impresoras:

        if (impre == '\'') & (cont == 0):
            cont = 1
            continue

        if (impre == '\'') & (cont == 1):
            conv_list_imp = ''.join(map(str, nom_carpeta))
            lista_conv_impre.append(conv_list_imp)
            nom_carpeta.clear()
            cont = 0

        if cont == 1:
            nom_carpeta.append(impre)

    return lista_conv_impre


# if __name__ == '__main__':

# obte_nom_traz_filt('C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico/2022_01_26_1548')


# IP = '15.83.20.247'
# ssh = conexiones.connectar_impresora(IP)
# descargar_archivos_carpeta('C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico','/tmp/HWQY/ScanAxis/Traces/2022-01-03', ssh)
# descargar_un_archivo('C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.2/Historico','total.txt','/tmp/HWQY/ScanAxis')
# conexiones.desconetar_impresora(ssh)
