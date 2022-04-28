
import pandas as pd
import numpy as np


def ver_traza(nom_traza):
    try:
        # Creamos el data frame
        df = pd.read_fwf(nom_traza, header=0, infer_nrows=1000)
        print('Data frame realizado con exito')
        return df

    except pd.errors.EmptyDataError:
        print('Traza vacia')



def anal_traza(df):
    ############ Variables a definir ######################################
    # Resolución encoder
    Res_enc = 19200
    # Radio polea en m
    Radio_polea_mot = 0.00725
    # Constante motor Vs
    Kmotor = 0.0805
    # Resistencia motor Ohm
    Rmotor = 2.68
    # Tensión motor V
    Vmot = 32
    # Limite Pwm
    Plim = 39000
    #######################################################################

    # Creamos un data frame con todos los datos que necesitamos.
    # Eliminamos las columnas vaciás.
    df = df.drop(['PSU_Rail(mV)', 'Voltage(mV)', 'Current(mA)', 'Current2(mA)', 'Event'], axis=1)

    # Modificamos los datos
    df = df.replace(to_replace='0 0x00000000', value='', regex=True)

    # Cambiamos nombre a la columna y pasamos a int64.
    df = df.rename(columns={df.columns[9]: 'Time'})
    df = df.astype({'Time': 'int64'})

    # Generamos una nueva columna desplazada hacia abajo
    df['Time_shift'] = df.Time.shift(periods=1, fill_value=0)

    # Nos dice el tipo de dato
    #df.info()

    # Calculamos el tiempo real en ms.
    df['Time_real_ms'] = ((df.Time - df.Time_shift) / 1000)

    # Ponemos a 0 el primer valor
    df.at[0, 'Time_real_ms'] = 0

    # Hacemos nueva columna acumulativa.
    df['Time_real_ms_cusum'] = df['Time_real_ms'].cumsum()

    # Hacemos nueva columna ref.position(m)
    df['RefPosicion_m'] = df.refPos / Res_enc * 25.4 / 1000

    # Hacemos nueva columna Real.position(m)
    df['RealPosicion_m'] = df.readPos / Res_enc * 25.4 / 1000

    # Hacemos nueva columna Ref. Speed(m/s)
    df['RefSpeed_ms'] = df.refSpeed / Res_enc * 25.4 / 1000 / 0.0012

    # Hacemos nueva columna Real. Speed(m/s)
    df['RealSpeed_ms'] = df.readSpeed / Res_enc * 25.4 / 1000 / 0.0012

    # Hacemos nueva columna Ref.Acceleration(g)
    df['RefSpeed_shift'] = df.RefSpeed_ms.shift(periods=1, fill_value=0)
    df['RefAcel_g'] = ((df.RefSpeed_ms - df.RefSpeed_shift) * 1000 / 1.2) / 9.81

    # Hacemos nueva columna Real.Acceleration(g)
    df['RealSpeed_shift'] = df.RealSpeed_ms.shift(periods=9, fill_value=0)
    df['Tim_rea_ms_cu_sh'] = df.Time_real_ms_cusum.shift(periods=9, fill_value=0)
    df['RealAcel_g'] = ((df.RealSpeed_ms - df.RealSpeed_shift) * 1000 / (
            df.Time_real_ms_cusum - df.Tim_rea_ms_cu_sh)) / 9.81
    df = df.fillna(0)

    # Hacemos nueva columna Ref.w(rad/s)
    df['Ref_w'] = df.RefSpeed_ms / Radio_polea_mot

    # Hacemos nueva columna Real.w(rad/s)
    df['Real_w'] = df.RealSpeed_ms / Radio_polea_mot

    # Hacemos nueva columna Corriente(A)
    df['Corriente'] = (df.Pwm * Vmot / Plim - Kmotor * df.Real_w) / Rmotor

    # Hacemos nueva columna Tension Motor (v)
    df['Tensi_Mot'] = df.Pwm * Vmot / Plim

    # Incluimos al data frame otra columna para calcular el % de la velocidad en SLEW
    df['RIPPLE'] = abs(((df.readSpeed - df.refSpeed) / df.refSpeed) * 100)

    # Incluimos al data frame otra columna para la sobre oscilación.
    df['SOBRE'] = ((df.readSpeed - df.refSpeed) / df.refSpeed) * 100

    # Incluimos al data frame otra columna con corriente RMS:
    df['corie_RMS'] = (df.Corriente) * (df.Corriente)

    # Incluimos al data frame otra columna con tensión RMS:
    df['Tensi_Mot_RMS'] = (df.Tensi_Mot) * (df.Tensi_Mot)

    # Incluimos en el data frame otra columna para calcular el retardo que hay entre la vel.real y la vel.teo. Ciclo positivo:
    max_ref_Speed = df['RefSpeed_ms'].max()
    df['Delay'] = np.where((0.85 * max_ref_Speed < df.RefSpeed_ms) & (0.9 * max_ref_Speed > df.RefSpeed_ms), 1, np.nan)
    fil_cont = 0
    for fil in df.Delay:
        if fil == 1:
            df.loc[fil_cont, 'Delay'] = df.loc[fil_cont, 'RefSpeed_ms']
            fil_cont += 1
        else:
            fil_cont += 1

    max_ref_Speed_085 = df['Delay'].max()
    min_ref_Speed_085 = df['Delay'].min()
    df['Delay_real'] = np.where((df.RealSpeed_ms > min_ref_Speed_085) & (df.RealSpeed_ms < max_ref_Speed_085), 1,
                                np.nan)
    fil_cont = 0
    for fil in df.Delay_real:
        if fil == 1:
            df.loc[fil_cont, 'Delay_real'] = df.loc[fil_cont, 'RealSpeed_ms']
            fil_cont += 1
        else:
            fil_cont += 1
    # Incluimos en el data frame otra columna para calcular el retardo que hay entre la vel.real y la vel.teo. Ciclo negativo:
    min_ref_Speed = df['RefSpeed_ms'].min()
    df['Delay_neg'] = np.where((0.85 * min_ref_Speed > df.RefSpeed_ms) & (0.9 * min_ref_Speed < df.RefSpeed_ms), 1,
                               np.nan)
    fil_cont = 0
    for fil in df.Delay_neg:
        if fil == 1:
            df.loc[fil_cont, 'Delay_neg'] = df.loc[fil_cont, 'RefSpeed_ms']
            fil_cont += 1
        else:
            fil_cont += 1

    max_ref_Speed_085 = df['Delay_neg'].max()
    min_ref_Speed_085 = df['Delay_neg'].min()
    df['Delay_real_neg'] = np.where((df.RealSpeed_ms > min_ref_Speed_085) & (df.RealSpeed_ms < max_ref_Speed_085), 1,
                                    np.nan)
    fil_cont = 0
    for fil in df.Delay_real_neg:
        if fil == 1:
            df.loc[fil_cont, 'Delay_real_neg'] = df.loc[fil_cont, 'RealSpeed_ms']
            fil_cont += 1
        else:
            fil_cont += 1

    # Creamos dos data frame para separar el ciclo positivo y el negativo. Estos data frame se usarán a posterior.

    cont = 0
    ciclo_pos = 0
    ciclo_neg = 0

    for pos in range(len(df)):
        x = df.iloc[pos, 6]

        # Buscamos el fin del ciclo positivo.
        if x == 'DECEL':
            cont = 1
        if (x == 'HOLD' and cont == 1) or (x == 'OFF' and cont == 1):
            ciclo_pos = df.head(pos)
            ciclo_neg = df.tail(len(df) - pos)
            break

    # Hacemos una tabla para calcular el % del error de la velocidad en SLEW
    # Paso 1/2
    SLEW_pos = ciclo_pos.loc[:, 'State'] == 'SLEW'
    df_SLEW_pos = ciclo_pos.loc[SLEW_pos]

    SLEW_neg = ciclo_neg.loc[:, 'State'] == 'SLEW'
    df_SLEW_neg = ciclo_neg.loc[SLEW_neg]

    # Paso 2/2
    # Eliminados las 30 primeras lineas para asegurar la estabilidad.
    df_SLEW_pos_30 = df_SLEW_pos[30:]
    Ripple_pos = pd.pivot_table(df_SLEW_pos_30, index=["State"], values=["RIPPLE"], aggfunc=[max], margins=True)

    df_SLEW_neg_30 = df_SLEW_neg[30:]
    Ripple_neg = pd.pivot_table(df_SLEW_neg_30, index=["State"], values=["RIPPLE"], aggfunc=[max], margins=True)

    # Calculo de la sobreoscilación.
    # Paso 1/2
    # Seleccionamos el estado SLEW
    SLEW_pos_sob = ciclo_pos.loc[:, 'State'] == 'SLEW'
    df_SLEW_pos_sob = ciclo_pos.loc[SLEW_pos_sob]

    SLEW_neg_sob = ciclo_neg.loc[:, 'State'] == 'SLEW'
    df_SLEW_neg_sob = ciclo_neg.loc[SLEW_neg_sob]

    # Paso 2/2
    # Nos quedamos con las 30 primeras filas.
    Sob_30_pos = df_SLEW_pos_sob.head(30)
    Sob_30_sol_pos = pd.pivot_table(Sob_30_pos, index=["State"], values=["SOBRE"], aggfunc=[max], margins=True)

    Sob_30_neg = df_SLEW_neg_sob.head(30)
    Sob_30_sol_neg = pd.pivot_table(Sob_30_neg, index=["State"], values=["SOBRE"], aggfunc=[max], margins=True)

    # Calculo del tiempo de estabilización:
    # Seleccionamos SLEW Y ACCEL ciclo positivo.
    Slew_Accel_S = ciclo_pos.loc[:, 'State'] == 'SLEW'
    Slew_Accel_A = ciclo_pos.loc[:, 'State'] == 'ACCEL'
    Tot = Slew_Accel_S + Slew_Accel_A
    df_SLEW_ACCEL = ciclo_pos.loc[Tot]

    # Calculamos el Max, que sera nuestra referencia.
    Max_SLEW_ACCEL = pd.pivot_table(df_SLEW_ACCEL, index=["State"], values=["refSpeed"], aggfunc=[max], margins=True)
    Max_SLEW_ACCEL_dato = Max_SLEW_ACCEL.iloc[1, 0].tolist()

    # Seleccionamos SLEW Y ACCEL ciclo negativo.
    Slew_Accel_S_neg = ciclo_neg.loc[:, 'State'] == 'SLEW'
    Slew_Accel_A_neg = ciclo_neg.loc[:, 'State'] == 'ACCEL'
    Tot = Slew_Accel_S_neg + Slew_Accel_A_neg
    df_SLEW_ACCEL_neg = ciclo_neg.loc[Tot]

    # Calculamos el Max, que sera nuestra referencia.
    Max_SLEW_ACCEL_neg = pd.pivot_table(df_SLEW_ACCEL_neg, index=["State"], values=["refSpeed"], aggfunc=[max],
                                        margins=True)
    Max_SLEW_ACCEL_dato_neg = Max_SLEW_ACCEL_neg.iloc[1, 0].tolist()

    # Incluimos al data frame otra columna para la distancia de estabilización. Ciclo positivo.
    df['Tiem_est_sol'] = abs((df.readSpeed - Max_SLEW_ACCEL_dato) / Max_SLEW_ACCEL_dato)
    df['Tiem_est'] = np.where(abs((df.readSpeed - Max_SLEW_ACCEL_dato) / Max_SLEW_ACCEL_dato) <= 0.050, 1, 0)

    fil_ind = 0

    for fil in df.Tiem_est:

        if fil == 1:
            df.loc[fil_ind, 'Tiem_est'] = df.loc[fil_ind - 1, 'Tiem_est'] + 1
            fil_ind += 1
            continue

        if fil == 0:
            df.loc[fil_ind, 'Tiem_est'] = 0
            fil_ind += 1
            continue

    # Incluimos al data frame otra columna para la distancia de estabilización. Ciclo negativo.
    df['Tiem_est_sol_neg'] = abs((df.readSpeed - Max_SLEW_ACCEL_dato_neg) / Max_SLEW_ACCEL_dato_neg)
    df['Tiem_est_neg'] = np.where(abs((df.readSpeed - Max_SLEW_ACCEL_dato_neg) / Max_SLEW_ACCEL_dato_neg) <= 0.050, 1,
                                  0)
    fil_ind = 0

    for fil in df.Tiem_est_neg:

        if fil == 1:
            df.loc[fil_ind, 'Tiem_est_neg'] = df.loc[fil_ind - 1, 'Tiem_est_neg'] + 1
            fil_ind += 1
            continue

        if fil == 0:
            df.loc[fil_ind, 'Tiem_est_neg'] = 0
            fil_ind += 1
            continue

    # Realizamos otra columna para calcular la distancia. Ciclo Positivo.
    df['Dist_Sobre'] = np.where(df.Tiem_est == 1, 1, 0)

    fil_cont = 0
    valor = 0

    for fil in df.Dist_Sobre:
        if fil == 1:
            valor = df.loc[fil_cont, 'readPos'] / 19200 * 25.4
            df.loc[fil_cont, 'Dist_Sobre'] = valor
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Dist_Sobre'] = valor
            fil_cont += 1

    # Realizamos otra columna para calcular la distancia.Ciclo Negativo.
    df['Dist_Sobre_neg'] = np.where(df.Tiem_est_neg == 1, 1, 0)

    fil_cont = 0
    valor = 0

    for fil in df.Dist_Sobre_neg:
        if fil == 1:
            valor = df.loc[fil_cont, 'readPos'] / 19200 * 25.4
            df.loc[fil_cont, 'Dist_Sobre_neg'] = valor
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Dist_Sobre_neg'] = valor
            fil_cont += 1

    # Sacamos las distancias y las restamos. Ciclo Positivo.

    fil_cont = 0
    dist_30 = 0
    dist_SLEW = 0

    for fil in df.Tiem_est:
        if fil == 30:
            dist_30 = df.loc[fil_cont, 'Dist_Sobre']
            fil_cont += 1
            break
        else:
            fil_cont += 1

    dist_SLEW = (df_SLEW_pos_sob.iloc[0, 3].tolist()) / 19200 * 25.4

    dist_estabili = dist_30 - dist_SLEW

    # Sacamos las distancias y las restamos. Ciclo Negativo.

    fil_cont = 0
    dist_30_neg = 0
    dist_SLEW_neg = 0

    for fil in df.Tiem_est_neg:
        if fil == 30:
            dist_30_neg = df.loc[fil_cont, 'Dist_Sobre_neg']
            fil_cont += 1
            break
        else:
            fil_cont += 1

    dist_SLEW_neg = (df_SLEW_neg_sob.iloc[0, 3].tolist()) / 19200 * 25.4

    dist_estabili_neg = dist_SLEW_neg - dist_30_neg

    # Calculo del retardo que hay entre la vel.real y la vel.teo:
    # Calculo del tiempo de referencia. Ciclo positivo.
    fil_cont = 0
    for fil in df.Delay:
        if np.isnan(fil):
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Delay'] = df.loc[fil_cont, 'Time_real_ms_cusum']
            fil_cont += 1

    # Calculo del tiempo real.
    fil_cont = 0
    for fil in df.Delay_real:
        if np.isnan(fil):
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Delay_real'] = df.loc[fil_cont, 'Time_real_ms_cusum']
            fil_cont += 1

    # Calculo del tiempo de referencia. Ciclo negativo.
    fil_cont = 0
    for fil in df.Delay_neg:
        if np.isnan(fil):
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Delay_neg'] = df.loc[fil_cont, 'Time_real_ms_cusum']
            fil_cont += 1

    # Calculo del tiempo real.
    fil_cont = 0
    for fil in df.Delay_real_neg:
        if np.isnan(fil):
            fil_cont += 1
        else:
            df.loc[fil_cont, 'Delay_real_neg'] = df.loc[fil_cont, 'Time_real_ms_cusum']
            fil_cont += 1

    # Calculo corriente RMS:
    # Ciclo positivo
    Slew_Accel_D = ciclo_pos.loc[:, 'State'] == 'DECEL'
    Tot = Slew_Accel_S + Slew_Accel_A + Slew_Accel_D
    df_SLEW_ACCEL_DECEL = ciclo_pos.loc[Tot]

    # Ciclo negativo
    Slew_Accel_D_neg = ciclo_neg.loc[:, 'State'] == 'DECEL'
    Tot_neg = Slew_Accel_S_neg + Slew_Accel_A_neg + Slew_Accel_D_neg
    df_SLEW_ACCEL_DECEL_neg = ciclo_neg.loc[Tot_neg]

    # Resultados:
    # Ciclo positivo
    # Calculo del PWM:
    pwm = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Pwm"], aggfunc=[max, min, np.mean],
                         margins=True)
    # Calculo pico de aceleración:
    pic_acc = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["RealAcel_g"], aggfunc=[max, min, np.mean],
                             margins=True)
    # Calculo pico de corriente:
    corient = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Corriente"], aggfunc=[max, min, np.mean],
                             margins=True)
    # Calculo pico de corriente slew sin los 30 primeros valores.
    corient_30 = pd.pivot_table(df_SLEW_pos_30, index=["State"], values=["Corriente"], aggfunc=[max, min, np.mean],
                                margins=True)
    # Calculo corriente RMS:
    corient_RMS = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["corie_RMS"],
                                 aggfunc=[max, min, np.mean],
                                 margins=True)
    # Calculo Motor Tensión:
    mot_tensi_pos = pd.pivot_table(df_SLEW_pos_30, index=["State"], values=["Tensi_Mot"], aggfunc=[max, min, np.mean],
                                   margins=True)
    # Calculo tensión RMS:
    tens_RMS_posi = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Tensi_Mot_RMS"],
                                   aggfunc=[max, min, np.mean],
                                   margins=True)
    # Ciclo negativo:
    # Calculo del PWM:
    pwm_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Pwm"], aggfunc=[max, min, np.mean],
                             margins=True)
    # Calculo pico de aceleración:
    pic_acc_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["RealAcel_g"],
                                 aggfunc=[max, min, np.mean],
                                 margins=True)
    # Calculo pico de corriente:
    corient_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Corriente"],
                                 aggfunc=[max, min, np.mean],
                                 margins=True)
    # Calculo pico de corriente slew sin los 30 primeros valores.
    corient_30_neg = pd.pivot_table(df_SLEW_neg_30, index=["State"], values=["Corriente"], aggfunc=[max, min, np.mean],
                                    margins=True)
    # Calculo corriente RMS:
    corient_RMS_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["corie_RMS"],
                                     aggfunc=[max, min, np.mean],
                                     margins=True)
    # Calculo Motor Tensión:
    mot_tensi_neg = pd.pivot_table(df_SLEW_neg_30, index=["State"], values=["Tensi_Mot"], aggfunc=[max, min, np.mean],
                                   margins=True)
    # Calculo tensión RMS:
    tens_RMS_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Tensi_Mot_RMS"],
                                  aggfunc=[max, min, np.mean],
                                  margins=True)

    # Creamos dos diccionario, para sacar las variables.
    # Ciclo positivo:
    dic_var_pos = {'pwm_slew_pos': pwm.iloc[2, 2].tolist(), 'pwm_max_pos': pwm.iloc[3, 0].tolist(), 'rip_pos': Ripple_pos.iloc[0, 0].tolist(),
                   'sobre_pos': Sob_30_sol_pos.iloc[0, 0].tolist(), 'estab_pos': dist_estabili, 'acc_max_pos': pic_acc.iloc[0, 0].tolist(),
                   'int_max_pos':corient.iloc[3, 0].tolist(), 'int_slew_pos': corient_30.iloc[0, 2].tolist(), 'corient_RMS_pos': np.sqrt(corient_RMS.iloc[3, 2].tolist()),
                   'mot_ten_pos': mot_tensi_pos.iloc[0, 2].tolist(), 'tens_RMS_pos': np.sqrt(tens_RMS_posi.iloc[3, 2].tolist()),
                   'mot_retra_pos': df['Delay_real'].min() - df['Delay'].min()}

    # Ciclo negativo:
    dic_var_neg = {'pwm_slew_neg': pwm_neg.iloc[2, 2].tolist(), 'pwm_max_neg': pwm_neg.iloc[3, 1].tolist(), 'rip_neg': Ripple_neg.iloc[0, 0].tolist(),
                   'sobre_neg': Sob_30_sol_neg.iloc[0, 0].tolist(), 'estab_neg': dist_estabili_neg, 'acc_max_neg': pic_acc_neg.iloc[3, 1].tolist(),
                   'int_max_neg': corient_neg.iloc[3, 1].tolist(), 'int_slew_neg': corient_30_neg.iloc[0, 2].tolist(),
                   'coriente_RMS_neg': -np.sqrt(corient_RMS_neg.iloc[3, 2].tolist()), 'mot_ten_neg': mot_tensi_neg.iloc[0, 2].tolist(),
                   'tensi_RMS_neg': -np.sqrt(tens_RMS_neg.iloc[3, 2].tolist()), 'mot_retra_neg': df['Delay_real_neg'].min() - df['Delay_neg'].min()}

    return df, dic_var_pos, dic_var_neg


def anal_traza_simp(df):

    ############ Variables a definir ######################################
    # Resolución encoder
    Res_enc = 19200
    # Tensión motor V
    Vmot = 32
    # Limite Pwm
    Plim = 39000
    #######################################################################

    # Creamos un data frame con todos los datos que necesitamos.
    # Eliminamos las columnas vacías.
    df = df.drop(['PSU_Rail(mV)', 'Voltage(mV)', 'Current(mA)', 'Current2(mA)', 'Event'], axis=1)

    # Modificamos los datos
    df = df.replace(to_replace='0 0x00000000', value='', regex=True)

    # Cambiamos nombre a la columna y pasamos a int64.
    df = df.rename(columns={df.columns[9]: 'Time'})
    df = df.astype({'Time': 'int64'})

    # Generamos una nueva columna desplazada hacia abajo
    df['Time_shift'] = df.Time.shift(periods=1, fill_value=0)

    # Nos dice el tipo de dato
    # df.info()

    # Calculamos el tiempo real en ms.
    df['Time_real_ms'] = ((df.Time - df.Time_shift) / 1000)

    # Ponemos a 0 el primer valor
    df.at[0, 'Time_real_ms'] = 0

    # Hacemos nueva columna acumulativa.
    df['Time_real_ms_cusum'] = df['Time_real_ms'].cumsum()

    # Hacemos nueva columna ref.position(m)
    df['RefPosicion_m'] = df.refPos / Res_enc * 25.4 / 1000

    # Hacemos nueva columna Real.position(m)
    df['RealPosicion_m'] = df.readPos / Res_enc * 25.4 / 1000

    # Hacemos nueva columna Ref. Speed(m/s)
    df['RefSpeed_ms'] = df.refSpeed / Res_enc * 25.4 / 1000 / 0.0012

    # Hacemos nueva columna Real. Speed(m/s)
    df['RealSpeed_ms'] = df.readSpeed / Res_enc * 25.4 / 1000 / 0.0012

    # Hacemos nueva columna Ref.Acceleration(g)
    df['RefSpeed_shift'] = df.RefSpeed_ms.shift(periods=1, fill_value=0)
    df['RefAcel_g'] = ((df.RefSpeed_ms - df.RefSpeed_shift) * 1000 / 1.2) / 9.81

    # Hacemos nueva columna Real.Acceleration(g)
    df['RealSpeed_shift'] = df.RealSpeed_ms.shift(periods=9, fill_value=0)
    df['Tim_rea_ms_cu_sh'] = df.Time_real_ms_cusum.shift(periods=9, fill_value=0)
    # He puesto un tiempo constante 10.8.
    df['RealAcel_g'] = ((df.RealSpeed_ms - df.RealSpeed_shift) * 1000 / 10.8) / 9.81
    df = df.fillna(0)

    # Hacemos nueva columna Tension Motor (v)
    df['Tensi_Mot'] = df.Pwm * Vmot / Plim

    # Incluimos al data frame otra columna con tensión RMS:
    df['Tensi_Mot_RMS'] = df.Tensi_Mot * df.Tensi_Mot

    # Cálculo del MSE para la aceleración:
    # df['Residual_MSE'] = df.RefAcel_g - df.RealAcel_g
    # df['Resi_cuadra'] = df.Residual_MSE * df.Residual_MSE


    # Creamos dos data frame para separar el ciclo positivo y el negativo. Estos data frame se usarán a posterior.

    cont = 0
    ciclo_pos = 0
    ciclo_neg = 0

    for pos in range(len(df)):
        x = df.iloc[pos, 6]

        # Buscamos el fin del ciclo positivo.
        if x == 'DECEL':
            cont = 1
        if (x == 'HOLD' and cont == 1) or (x == 'OFF' and cont == 1):
            ciclo_pos = df.head(pos)
            ciclo_neg = df.tail(len(df) - pos)
            break

     # Seleccionamos SLEW Y ACCEL. Ciclo positivo.
    Slew_Accel_S = ciclo_pos.loc[:, 'State'] == 'SLEW'
    Slew_Accel_A = ciclo_pos.loc[:, 'State'] == 'ACCEL'
    Tot = Slew_Accel_S + Slew_Accel_A
    df_SLEW_ACCEL = ciclo_pos.loc[Tot]

    # Seleccionamos SLEW, ACCEL y DECEL. Ciclo positivo.
    Slew_Accel_D = ciclo_pos.loc[:, 'State'] == 'DECEL'
    Tot = Slew_Accel_S + Slew_Accel_A + Slew_Accel_D
    df_SLEW_ACCEL_DECEL = ciclo_pos.loc[Tot]

    # Seleccionamos SLEW Y ACCEL ciclo negativo.
    Slew_Accel_S_neg = ciclo_neg.loc[:, 'State'] == 'SLEW'
    Slew_Accel_A_neg = ciclo_neg.loc[:, 'State'] == 'ACCEL'
    Tot = Slew_Accel_S_neg + Slew_Accel_A_neg
    df_SLEW_ACCEL_neg = ciclo_neg.loc[Tot]

    # Seleccionamos SLEW, ACCEL y DECEL. Ciclo negativo.
    Slew_Accel_D_neg = ciclo_neg.loc[:, 'State'] == 'DECEL'
    Tot_neg = Slew_Accel_S_neg + Slew_Accel_A_neg + Slew_Accel_D_neg
    df_SLEW_ACCEL_DECEL_neg = ciclo_neg.loc[Tot_neg]

    # Resultados:

    # Ciclo positivo
    # Calculo del PWM:
    pwm = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Pwm"], aggfunc=[max, min, np.mean],
                         margins=True)
    # Calculo tensión RMS:
    tens_RMS_posi = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Tensi_Mot_RMS"],
                                   aggfunc=[max, min, np.mean],
                                   margins=True)
    # Cálculo del MSE:
    # MSE_pos = pd.pivot_table(df_SLEW_ACCEL_DECEL, index=["State"], values=["Resi_cuadra"],
    #                               aggfunc=[max, min, np.mean],
    #                               margins=True)

    # Ciclo negativo:
    # Calculo del PWM:
    pwm_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Pwm"], aggfunc=[max, min, np.mean],
                             margins=True)

    # Calculo tensión RMS:
    tens_RMS_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Tensi_Mot_RMS"],
                                  aggfunc=[max, min, np.mean],
                                  margins=True)

    # Cálculo del MSE:
    # MSE_neg = pd.pivot_table(df_SLEW_ACCEL_DECEL_neg, index=["State"], values=["Resi_cuadra"],
    #                              aggfunc=[max, min, np.mean],
    #                              margins=True)

    # Creamos dos diccionario, para sacar las variables.
    # Ciclo positivo:
    dic_var_pos = {'pwm_slew_pos': pwm.iloc[2, 2].tolist(), 'pwm_max_pos': pwm.iloc[3, 0].tolist(), 'tens_RMS_pos': np.sqrt(tens_RMS_posi.iloc[3, 2].tolist()),
                   }

    # Ciclo negativo:
    dic_var_neg = {'pwm_slew_neg': pwm_neg.iloc[2, 2].tolist(), 'pwm_max_neg': pwm_neg.iloc[3, 1].tolist(), 'tensi_RMS_neg': -np.sqrt(tens_RMS_neg.iloc[3, 2].tolist()),
                   }

    return df.RefAcel_g, df.RealAcel_g, df.Pwm, df.Time_real_ms_cusum, dic_var_pos, dic_var_neg, df.State, df.RealPosicion_m


if __name__ == '__main__':

    df = ver_traza('2022-03-10-10-18-14_3832015.log')
    a = anal_traza_simp(df)
    print(df)
