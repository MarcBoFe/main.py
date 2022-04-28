import paramiko
import escritura_txt


# Establecemos la conexión con la impresora. Variable de entrada host=IP. Variable de salida la variable de conexión.

def connectar_impresora(host, port=22, user='root', password='socorro!'):
    # Realizamos conexión
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, user, password)
        print('Conexión realizada impresora', host)
        return ssh
    except TimeoutError:
        print('No he podido conectarme a la impresora {}'.format(host))

# Función para enviar comando. Variables de entrada comando y sesión. Devuelve dato Linux.

def enviar_comando(command, ssh):
    # stdin,stdout,stderr son las entradas, salidas y errores que devuelve Linux. La función exec_command ejecuta el comando definido.
    stdin, stdout, stderr = ssh.exec_command(command)
    # Devuelve un error si lo hay.
    my_error = stderr.readlines()

    if not my_error:
        codigo_list = stdout.readlines()
        # Codigo preparado por si se quiere sacar los ciclos totales.
        # dato_sal = codigo_list[0]
        # dato_sal.replace('\n', '')
        # return dato_sal

        list_sal = []
        for lis in codigo_list:
            dato_sal = lis.replace('\n', '')
            list_sal.append(dato_sal)

        return list_sal

    else:
        print('Compadre, hay un error: {}'.format(my_error))
        return 'linux_error'


# Función para desconectar sesión.

def desconetar_impresora(ssh):
    ssh.close()


# Comprueba el estado de la printer para ello restamos los ciclos. Variables de entrada en string ciclos iniciales y finales. Lista donde se quiere anotar.
# Variable de salida escribe el dato en la lista.

def comprobar_estado(ciclos_init, ciclos_final, lista):
    # Pasamos de string a int
    int_ciclos_init = int(ciclos_init)
    int_ciclos_final = int(ciclos_final)
    # Comprobamos estado.
    if (int_ciclos_final - int_ciclos_init) == 0:
        # Lo escribimos en la lista.
        escritura_txt.escribir_dato_lista('OFF', lista)
        # print('Esta impresora no funciona')
    else:
        escritura_txt.escribir_dato_lista('ON', lista)
        # print('Esta impresora  funciona')
