import matplotlib.pyplot as plt
import os

# Funcion para graficar los resultado.
# Var_ent: ciclo: dataframe del ciclo. Ejemplo:ciclo_pos. Var_x/y: variables a graficar. Ejemplo:'readPos' o 'Pwm'. Titulo del grafico.Ej:"Tabla de Marc"
# Var_sal: Graficas
import pandas as pd


def graficar(ciclo, var_x, var_y, titulo):
    ciclo.plot.line(x=var_x, y=var_y)
    plt.title(titulo)
    plt.xlabel(var_x)
    plt.ylabel(var_y)
    plt.grid(axis='y')
    plt.show()


# Esta función hace lo mismo que la anterior pero muestra dos gráficas a la vez.

def graficar_1(df, nom_traza):
    Pwm = df.Pwm.tolist()
    PwmLimit = df.PwmLimit.tolist()
    RefPosicion_m = df.RefPosicion_m.tolist()
    RealPosicion_m = df.RealPosicion_m.tolist()
    RefAcel_g = df.RefAcel_g.tolist()
    RealAcel_g = df.RealAcel_g.tolist()
    Tensi_Mot_RMS = df.Tensi_Mot_RMS.tolist()
    corie_RMS = df.corie_RMS.tolist()

    fig, axs = plt.subplots(2, 2)

    axs[0, 0].plot(Pwm, color="blue", label="Pwm")
    axs[0, 0].plot(PwmLimit, color="red", label="PwmLimit")
    axs[0, 0].set_title('Pwm')
    axs[0, 0].grid(True)
    axs[0, 0].legend(loc='upper left')

    axs[0, 1].plot(RefPosicion_m, color="blue", label="RefPosicion_m")
    axs[0, 1].plot(RealPosicion_m, color="red", label="RealPosicion_m")
    axs[0, 1].set_title('Posición')
    axs[0, 1].grid(True)
    axs[0, 1].legend(loc='upper left')

    axs[1, 0].plot(RefAcel_g, color="blue", label="RefAcel_g")
    axs[1, 0].plot(RealAcel_g, color="red", label="RealAcel_g")
    axs[1, 0].set_title('Aceleración')
    axs[1, 0].grid(True)
    axs[1, 0].legend(loc='upper left')

    axs[1, 1].plot(Tensi_Mot_RMS, color="blue", label="Tensi_Mot_RMS")
    # ax2[1, 1].plot(corie_RMS, color="red", label="corie_RMS")
    axs[1, 1].set_title('Tensión_RMS')
    axs[1, 1].grid(True)
    axs[1, 1].legend(loc='upper left')

    # Sacamos datos a excel.
    graf1_exp_ex = df.loc[:,
                   ['Pwm', 'PwmLimit', 'RefPosicion_m', 'RealPosicion_m', 'RefAcel_g', 'RealAcel_g', 'Tensi_Mot_RMS',
                    'corie_RMS']]

    # Cambiamos directorio para guardar en excel.
    dir_modo2 = 'C:\\Users\\BolosFM\\Documents\\HP Marc\\Documentos\\Python\\Prueba3.4\\Salida_datos'
    os.chdir(dir_modo2)

    graf1_exp_ex.to_excel(f'{nom_traza}.xlsx')

    plt.show()


def graficar_2(df1, df2, nom_traza1, nom_traza2):
    Pwm1 = df1.Pwm.tolist()
    Pwm2 = df2.Pwm.tolist()
    RefPosicion_m1 = df1.RefPosicion_m.tolist()
    RefPosicion_m2 = df2.RefPosicion_m.tolist()
    RealPosicion_m1 = df1.RealPosicion_m.tolist()
    RealPosicion_m2 = df2.RealPosicion_m.tolist()
    RefAcel_g1 = df1.RefAcel_g.tolist()
    RefAcel_g2 = df2.RefAcel_g.tolist()
    RealAcel_g1 = df1.RealAcel_g.tolist()
    RealAcel_g2 = df2.RealAcel_g.tolist()
    Tensi_Mot_RMS1 = df1.Tensi_Mot_RMS.tolist()
    Tensi_Mot_RMS2 = df2.Tensi_Mot_RMS.tolist()

    fig, axs = plt.subplots(2, 1)

    Pwm_MSE = (df1.Pwm - df2.Pwm)**2
    Pwm_MSE_list = Pwm_MSE.tolist()

    axs[0].plot(Pwm1, color="blue", label="Pwm{nom_traza1}")
    axs[0].plot(Pwm2, color="red", label="Pwm{nom_traza2}")
    axs[0].set_title('Pwm')
    axs[0].grid(True)
    axs[0].legend(loc='upper left')

    axs[1].plot(Pwm_MSE_list, color="blue", label="Pwm_MSE")
    axs[1].set_title('Pwm dif')
    axs[1].grid(True)
    axs[1].legend(loc='upper left')

    fig1, axs1 = plt.subplots(2, 1)

    RealPosicion_m_MSE = (df1.RealPosicion_m - df2.RealPosicion_m)**2
    RealPosicion_m_MSE_list = RealPosicion_m_MSE.tolist()

    axs1[0].plot(RealPosicion_m1, color="blue", label="RealPosicion_m1")
    axs1[0].plot(RealPosicion_m2, color="red", label="RealPosicion_m2")
    axs1[0].set_title('Posición')
    axs1[0].grid(True)
    axs1[0].legend(loc='upper left')

    axs1[1].plot(RealPosicion_m_MSE_list, color="blue", label="Posición Real MSE")
    axs1[1].set_title('Posición Real MSE')
    axs1[1].grid(True)
    axs1[1].legend(loc='upper left')

    fig2, axs2 = plt.subplots(2, 1)

    RealAcel_g_MSE = (df1.RealAcel_g - df2.RealAcel_g) ** 2
    RealAcel_g_MSE_list = RealAcel_g_MSE.tolist()

    axs2[0].plot(RealAcel_g1, color="blue", label="RealAcel_g1")
    axs2[0].plot(RealAcel_g2, color="red", label="RealAcel_g2")
    axs2[0].set_title('Aceleración')
    axs2[0].grid(True)
    axs2[0].legend(loc='upper left')

    axs2[1].plot(RealAcel_g_MSE_list, color="blue", label="RealAcel_g_MSE")
    axs2[1].set_title('Aceleración MSE')
    axs2[1].grid(True)
    axs2[1].legend(loc='upper left')

    plt.show()



def graf_gene_pwm(nom_ciclo, max_pos, max_neg, slew_pos, slew_neg, mse_ace, mse_dec, mse_slew):
    fig, axs = plt.subplots(4, 1)

    axs[0].plot(nom_ciclo, max_pos, color="blue", label="max_ciclo_pos")
    axs[0].plot(nom_ciclo, max_neg, color="red", label="max_ciclo_neg")
    axs[0].set_title('Maximos')
    axs[0].set_xticks('off')
    axs[0].legend(loc='upper left')
    # plt.xticks(rotation=90)
    # axs[0].grid(True)

    axs[1].plot(nom_ciclo, slew_pos, color="blue", label="slew_ciclo_pos")
    axs[1].plot(nom_ciclo, slew_neg, color="red", label="slew_ciclo_neg")
    axs[1].set_title('Slew')
    axs[1].legend(loc='upper left')
    axs[1].set_xticks('off')
    # plt.xticks(rotation=90)
    # axs[1].grid(True)

    axs[2].plot(nom_ciclo, mse_ace, color="blue", label="MSE_ace")
    axs[2].plot(nom_ciclo, mse_dec, color="red", label="MSE_dec")
    axs[2].set_title('MSE')
    axs[2].legend(loc='upper left')
    axs[2].set_xticks('off')

    axs[3].plot(nom_ciclo, mse_slew, color="blue", label="MSE_slew")
    axs[3].set_title('MSE_slew')
    axs[3].legend(loc='upper left')
    axs[3].set_xticks('off')


def graf_gene_sobre_esta(nom_ciclo, sobre_pos, sobre_neg, esta_pos, esta_neg):
    fig1, axs1 = plt.subplots(2, 1)

    axs1[0].plot(nom_ciclo, sobre_pos, color="blue", label="Sob_osci_pos")
    axs1[0].plot(nom_ciclo, sobre_neg, color="red", label="Sob_osci_neg")
    axs1[0].set_title('Sobre oscilación')
    axs1[0].set_xticks('off')
    axs1[0].legend(loc='upper left')
    # plt.xticks(rotation=90)
    # axs[0].grid(True)

    axs1[1].plot(nom_ciclo, esta_pos, color="blue", label="Esta_pos")
    axs1[1].plot(nom_ciclo, esta_neg, color="red", label="Esta_neg")
    axs1[1].set_title('Estabilización')
    axs1[1].legend(loc='upper left')
    axs1[1].set_xticks('off')
    # plt.xticks(rotation=90)
    # axs[1].grid(True)
