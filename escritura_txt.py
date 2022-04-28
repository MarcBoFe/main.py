
# Esta función abre impresoras_ip.txt y lee linea por linea el texto. Esta pensado para poner el nombre seguido de espacio y su IP.
# Devuelve una lista con el nombre y la IP.

def leer_txt():
    # Definimos la lista con las impresoras y IP´s.
    imp_ips = []
    # Leemos el .txt para obtener las IP`s y impresoras.
    with open("impresoras_ip.txt", "r") as archivo:
        # Vamos linea por linea leyendo los valores.
        for linea in archivo:
            # Separamos los espacios en vectores.
            descomponer_linea = linea.split(' ')
            # Quitamos /n del final.
            if len(descomponer_linea) >= 2:
                descomponer_linea[1] = descomponer_linea[1].replace('\n', '')
                # Añadimos la siguiente impresora a la lista.
                imp_ips.append(descomponer_linea)
    return imp_ips


# Pone un dato (string) a la derecha de la lista de entrada y lo escribe en ciclos_totales.txt
def escribir_dato(dato, dat_imp):
    # Escribe el dato a la derecha.
    dat_imp.append(dato)
    # Pasamos a string
    escrib_dato = ' '.join(dat_imp)
    # Escribe en el txt
    with open("ciclos_totales.txt", "a") as f:
        f.write(escrib_dato)


# Pone un dato (string) a la derecha de la lista de entrada
def escribir_dato_lista(dato, dat_imp):
    # Escribe el dato a la derecha.
    dat_imp.append(dato)
    # Pasamos a string
    ' '.join(dat_imp)


# if __name__ == '__main__':
    # imp_ips = leer_txt()
    # leer_txt()
    # escribir_total('aaa', imp_ips)
