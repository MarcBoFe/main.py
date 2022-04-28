import pandas as pd

import conexiones
import dibu_traza
import escritura_txt
import os
import gestion_archivos
import procesar_traza
import matplotlib.pyplot as plt
import numpy as np


def main():
    ### Variables generales ###
    nom_ciclos = []
    lista_trazas = []
    list_pos_max_pwm = []
    list_neg_max_pwm = []
    list_pos_slew_pwm = []
    list_neg_slew_pwm = []
    list_pos_riza = []
    list_neg_riza = []
    list_pos_sobre = []
    list_neg_sobre = []
    list_pos_estab = []
    list_neg_estab = []

    ace_ant = 0
    a = 'True'
    buf_ace_sol = []
    lis_ace_mse = []
    lis_dec_mse = []
    lis_slew_mse = []

    nom_direc = 0

    # Recogemos los valores. En el modo 1 lo descargamos. En el modo 2 desde la carpeta local.
    modo = input(
        '¿Que quieres hacer?. 1.Descargar trazas y analizar 2.Trazas descargadas y analizar 3.Analizar traza: ')

    if modo == '1':
        # Leemos lista impresoras_ip.txt
        imp_ips = escritura_txt.leer_txt()
        print('Leemos impresoras_ip.txt')

        # Realizamos conexión
        sesion = conexiones.connectar_impresora(imp_ips[0][1])

        print('Conexión realizada impresora:', imp_ips[0][0])

        # Creamos carpeta con el dia actual
        nom_direc = gestion_archivos.crear_carpeta_fecha(
            'C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.4/Trazas descargadas', imp_ips[0][0])

        Direc_bas = 'C:/Users/BolosFM/Documents/HP Marc/Documentos/Python/Prueba3.4/Trazas descargadas'
        Nue_direc = os.path.join(Direc_bas, nom_direc)

        # Leer todas las carpetas
        nom_carpetas = conexiones.enviar_comando('ls /tmp/HWQY/ScanAxis/Traces', sesion)

        # Preguntar que carpetas quieres descargar.

        print(f"Estas son todas las carpetas que hay,{nom_carpetas}")

        selec_carp = input(
            '¿Que carpetas quieres descargar?. Puedes copiar y pegar la liena anterior pero asegurate que esten las comillas:  ')

        # Crea una lista con las carpetas seleccionadas.
        lista_imp = gestion_archivos.conv_nom_impre(selec_carp)

        # Descargamos todos los archivos de las carpetas seleccionadas y la ponemos en la misma carpeta
        for lista in lista_imp:
            Dir_bas = '/tmp/HWQY/ScanAxis/Traces/'
            Nue_dir = Dir_bas + lista

            # Descargamos archivos de la carpeta selecionada.
            print('Descargando archivos.....')
            gestion_archivos.descargar_archivos_carpeta(Nue_direc, Nue_dir, sesion)

        # Desconectamos impresora.
        conexiones.desconetar_impresora(sesion)
        print('Impresora desconectada', imp_ips[0])

        # Obtenemos el número de la traza, a través del título del archivo y filtramos time.log
        nom_ciclos = gestion_archivos.obte_nom_traz_filt(Nue_direc)

        # Obtenemos el nombre de todos los archivos creados.
        lista_trazas = os.listdir(Nue_direc)

        # Cambiamos directorio de trabajo.
        dir_modo = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Trazas descargadas\\' + nom_direc
        os.chdir(dir_modo)

    if modo == '2':
        # Definimos el directorio donde trabaja el modo 2:
        dir_modo2 = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Trazas sin descarga'

        # Cambiamos directorio
        os.chdir(dir_modo2)

        # Leemos las carpetas que tenemos.
        nom_car_mod2 = os.listdir(dir_modo2)

        # Mostramos las carpetas que tenemos.
        print(f"Estas son todas las carpetas que hay,{nom_car_mod2}")
        nom_direc = input(
            '¿Que carpetas quieres procesar?. Puedes copiar y pegar la liena anterior pero asegurate de que NO esten las comillas:  ')

        # Redefinimos el directorio para poder aplicar las funciones.
        dir_modo2 = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Trazas sin descarga\\' + nom_direc
        os.chdir(dir_modo2)

        # Obtenemos el número de la traza, a través del título del archivo y filtramos time.log
        nom_ciclos = gestion_archivos.obte_nom_traz_filt(dir_modo2)

        # Obtenemos el nombre de todos los archivos creados.
        lista_trazas = os.listdir(dir_modo2)

    if modo == '3':
        print('En desarrollo..')

    # Una vez tenemos los datos vamos a procesar las trazas y sacar los valores que nos interesan.
    for traza in lista_trazas:
        # Verificamos que la traza tiene valores.
        df = procesar_traza.ver_traza(traza)

        # Sacamos los valores de la traza.
        if df is not None:

            # Procesamos.
            sol_df = procesar_traza.anal_traza_simp(df)

            # Sacamos los valores del diccionario.
            pwm_max_pos = abs(sol_df[4]['pwm_max_pos'])
            pwm_max_neg = abs(sol_df[5]['pwm_max_neg'])

            pwm_slew_pos = abs(sol_df[4]['pwm_slew_pos'])
            pwm_slew_neg = abs(sol_df[5]['pwm_slew_neg'])

            # Almacenamos en vector
            # Máximos del ciclo tanto a la ida como la vuelta.
            list_pos_max_pwm.append(pwm_max_pos)
            list_neg_max_pwm.append(pwm_max_neg)

            # Slew del ciclo tanto a la ida como la vuelta.
            list_pos_slew_pwm.append(pwm_slew_pos)
            list_neg_slew_pwm.append(pwm_slew_neg)

            # Cálculo de la desviación del control. Restamos aceleración de la traza actual - anterior, por tramos.
            # Cálculo del MSE
            if a == 'True':
                ace_act = sol_df[1]
                buf_ace_sol = (ace_act - ace_ant) ** 2
                ace_ant = ace_act
            if a != 'True':
                ace_act = sol_df[1]
                buf_ace_sol = (ace_act - ace_ant) ** 2
                ace_ant = ace_act
            a = not a

            # Hacemos un dataframe con el resultado y el estado.
            af = pd.DataFrame(list(zip(buf_ace_sol, sol_df[6])), columns=['acele', 'State'])

            # Eliminamos posibles resultados inf o nan
            af.replace([np.inf, -np.inf], 0, inplace=True)
            af.fillna(0)

            # Sacamos los valores del dataframe en una tabla dinámica.
            td_sol_ace = pd.pivot_table(af, index=["State"], values=["acele"], aggfunc=[np.mean],
                                        margins=True)

            # Sacamos el valor y lo pasamos a una lista.

            lis_ace_mse.append(td_sol_ace.iloc[0, 0])
            lis_dec_mse.append(td_sol_ace.iloc[1, 0])
            lis_slew_mse.append(td_sol_ace.iloc[3, 0])

            print('Procesando valores......')
        else:
            print(f'Hay una traza sin valores, borrala de la carpeta y vuelve a ejecutar.Traza: {traza}')
            break
    # Ponemos a 0 el primer elemento de la lista. Ya que el primer valor no es fiable.
    lis_ace_mse[0] = 0
    lis_dec_mse[0] = 0
    lis_slew_mse[0] = 0

    # Sacamos los valores al Excel:
    exp_ex = pd.DataFrame(list(zip(nom_ciclos, list_pos_max_pwm, list_neg_max_pwm, list_pos_slew_pwm, list_neg_slew_pwm,
                                   lis_ace_mse, lis_dec_mse, lis_slew_mse)), columns=['nom_ciclos',
                                                                                      'list_pos_max_pwm',
                                                                                      'list_neg_max_pwm',
                                                                                      'list_pos_slew_pwm',
                                                                                      'list_neg_slew_pwm',
                                                                                      'lis_ace_mse',
                                                                                      'lis_dec_mse',
                                                                                      'lis_slew_mse'])

    # Redefinimos el directorio donde se va a guardar el excel.
    dir_modo2 = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Salida_datos'
    os.chdir(dir_modo2)

    exp_ex.to_excel(f'{nom_direc}.xlsx')

    # Graficar resultados
    print('Graficando resultados......')

    dibu_traza.graf_gene_pwm(nom_ciclos, list_pos_max_pwm, list_neg_max_pwm, list_pos_slew_pwm, list_neg_slew_pwm,
                             lis_ace_mse, lis_dec_mse, lis_slew_mse)
    # dibu_traza.graf_gene_sobre_esta(nom_ciclos, list_pos_sobre, list_neg_sobre, list_pos_estab, list_neg_estab)

    plt.show()

    cicl_comp = []

    while cicl_comp != 'END':

        # Analisis de datos:
        print('Apunta el numero de ciclo que quieras comparar, se parado por coma')
        cicl_comp = input()
        nom_tra = cicl_comp.split(',')

        # Comprobamos que las trazas existen:
        num_core = False
        num1 = False
        num2 = False

        if len(nom_tra) == 1:
            for comp_nom_ciclo in nom_ciclos:
                if nom_tra[0] == comp_nom_ciclo:
                    num_core = True

        if len(nom_tra) == 2:
            for comp_nom_ciclo in nom_ciclos:
                if nom_tra[0] == comp_nom_ciclo:
                    num1 = True
                if nom_tra[1] == comp_nom_ciclo:
                    num2 = True
                if num1 and num2 is True:
                    num_core = True

        if num_core:
            # Decidimos la carpeta de trabajo en función del modo.
            if modo == '1':
                dir_modo = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Trazas descargadas\\' + nom_direc
                os.chdir(dir_modo)
            if modo == '2':
                dir_modo2 = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Trazas sin descarga\\' + nom_direc
                os.chdir(dir_modo2)

            # Entendemos que se quiere mirar una única traza.
            if (len(nom_tra) == 1) & (cicl_comp != 'END'):
                cont = 0

                for pos_traza in nom_ciclos:
                    # Pasar a int
                    int_pos_traza = int(pos_traza)
                    int_nom_traza = int(nom_tra[0])

                    # Buscamos la traza que queremos.
                    if int_pos_traza == int_nom_traza:
                        nom_traza_sel = lista_trazas[cont]
                        an1 = procesar_traza.ver_traza(nom_traza_sel)
                        if an1 is not None:
                            an1 = procesar_traza.anal_traza(an1)
                            dibu_traza.graficar_1(an1[0], lista_trazas[cont])
                            nom_tra = 0
                            break
                        else:
                            print('Traza sin valor')
                    else:
                        cont += 1

            # Se quieren comparar dos trazas.
            elif (len(nom_tra) == 2) & (cicl_comp != 'END'):
                cont = 0
                nom_traza_sel = []
                traz_graf = []
                a = 0
                salir = True

                while (len(traz_graf) <= 2) & (salir is True):
                    cont = 0
                    for pos_traza in nom_ciclos:
                        # Pasar a int
                        int_pos_traza = int(pos_traza)
                        int_nom_traza = int(nom_tra[a])

                        # Buscamos la traza que queremos.
                        if int_pos_traza == int_nom_traza:
                            traz_graf.append(lista_trazas[cont])
                            a += 1

                        # Si tenemos las dos trazas que queremos.
                        if len(traz_graf) == 2:

                            an2 = procesar_traza.ver_traza(traz_graf[0])
                            an3 = procesar_traza.ver_traza(traz_graf[1])

                            if an2 is not None:
                                if an3 is not None:
                                    an2 = procesar_traza.anal_traza(an2)
                                    an3 = procesar_traza.anal_traza(an3)
                                    dibu_traza.graficar_2(an2[0], an3[0], traz_graf[0], traz_graf[1])
                                    nom_tra = 0
                                    an2 = 0
                                    an3 = 0
                                    salir = False
                                    break
                                else:
                                    print(f'Traza{traz_graf[1]} sin valor')

                            else:
                                print(f'Traza{traz_graf[0]} sin valor')

                            break

                        else:
                            cont += 1

            elif cicl_comp != 'END':
                print('Solo podemos poner 1 o 2 valores')
        else:
            print('Números incorrectos')


if __name__ == '__main__':
    main()
