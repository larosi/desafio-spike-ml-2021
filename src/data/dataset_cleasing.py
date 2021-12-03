# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 16:03:58 2021

@author: Mico
"""

import pandas as pd
import argparse

def get_arguments():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--precipitaciones',
                           type=str,
                           default="data/raw/precipitaciones.csv",
                           help='Path to raw precipitaciones.csv')
    
    my_parser.add_argument('--banco_central',
                           type=str,
                           default="data/raw/banco_central.csv",
                           help='Path to raw banco_central.csv')
    
    my_parser.add_argument('--precio_leche',
                           type=str,
                           default="data/raw/precio_leche.csv",
                           help='Path to raw precio_leche.csv')
    
    my_parser.add_argument('--output_data',
                           type=str,
                           default="data/processed/precio_leche.csv",
                           help='Path to clean precio_leche.csv')
    
    return my_parser.parse_args()


""" Datos y limpieza de Datos"""
args = get_arguments()

precipitaciones_path = args.precipitaciones
banco_central_path = args.banco_central
precio_leche_path = args.precio_leche
precio_leche_output_path = args.output_data

month_dict = {'ene': 1,
              'feb': 2,
              'mar': 3,
              'abr': 4,
              'may': 5,
              'jun': 6,
              'jul': 7,
              'ago': 8,
              'sep': 9,
              'oct': 10,
              'nov': 11,
              'dic': 12}


""" Precipitaciones """

precipitaciones = pd.read_csv(precipitaciones_path)#[mm]
precipitaciones['date'] = pd.to_datetime(precipitaciones['date'], format = '%Y-%m-%d')
precipitaciones = precipitaciones.sort_values(by = 'date', ascending = True).reset_index(drop = True)

precipitaciones[precipitaciones.isna().any(axis=1)] 

precipitaciones[precipitaciones.duplicated(subset = 'date', keep = False)] #ni repetidos

regiones = ['Coquimbo', 'Valparaiso', 'Metropolitana_de_Santiago',
       'Libertador_Gral__Bernardo_O_Higgins', 'Maule', 'Biobio',
       'La_Araucania', 'Los_Rios']

""" Banco central """

banco_central = pd.read_csv(banco_central_path)

banco_central['Periodo'] = banco_central['Periodo'].apply(lambda x: x[0:10])

banco_central['Periodo'] = pd.to_datetime(banco_central['Periodo'], format = '%Y-%m-%d', errors = 'coerce')

banco_central[banco_central.duplicated(subset = 'Periodo', keep = False)] #repetido se elimina

banco_central.drop_duplicates(subset = 'Periodo', inplace = True)
banco_central = banco_central[~banco_central.Periodo.isna()]

def convert_int(x):
    return int(x.replace('.', ''))

cols_pib = [x for x in list(banco_central.columns) if 'PIB' in x]
cols_pib.extend(['Periodo'])
banco_central_pib = banco_central[cols_pib]
banco_central_pib = banco_central_pib.dropna(how = 'any', axis = 0)

for col in cols_pib:
    if col == 'Periodo':
        continue
    else:
        banco_central_pib[col] = banco_central_pib[col].apply(lambda x: convert_int(x))

banco_central_pib.sort_values(by = 'Periodo', ascending = True)

def to_100(x): #mirando datos del bc, pib existe entre ~85-120 - igual esto es cm (?)
    x = x.split('.')
    if x[0].startswith('1'): #es 100+
        if len(x[0]) >2:
            return float(x[0] + '.' + x[1])
        else:
            x = x[0]+x[1]
            return float(x[0:3] + '.' + x[3:])
    else:
        if len(x[0])>2:
            return float(x[0][0:2] + '.' + x[0][-1])
        else:
            x = x[0] + x[1]
            return float(x[0:2] + '.' + x[2:])

        
cols_imacec = [x for x in list(banco_central.columns) if 'Imacec' in x]
cols_imacec.extend(['Periodo'])
banco_central_imacec = banco_central[cols_imacec]
banco_central_imacec = banco_central_imacec.dropna(how = 'any', axis = 0)

for col in cols_imacec:
    if col == 'Periodo':
        continue
    else:
        banco_central_imacec[col] = banco_central_imacec[col].apply(lambda x: to_100(x))
        assert(banco_central_imacec[col].max()>100)
        assert(banco_central_imacec[col].min()>30)

banco_central_imacec.sort_values(by = 'Periodo', ascending = True)

banco_central_iv = banco_central[['Indice_de_ventas_comercio_real_no_durables_IVCM', 'Periodo']]
banco_central_iv = banco_central_iv.dropna() # -unidades? #parte 
banco_central_iv = banco_central_iv.sort_values(by = 'Periodo', ascending = True)

banco_central_iv['num'] = banco_central_iv.Indice_de_ventas_comercio_real_no_durables_IVCM.apply(lambda x: to_100(x))

banco_central_num = pd.merge(banco_central_pib, banco_central_imacec, on = 'Periodo', how = 'inner')
banco_central_num = pd.merge(banco_central_num, banco_central_iv, on = 'Periodo', how = 'inner')

""" precio leche """

precio_leche = pd.read_csv(precio_leche_path)
precio_leche.rename(columns = {'Anio': 'ano', 'Mes': 'mes_pal'}, inplace = True) # precio = nominal, sin iva en clp/litro

# FIXME: locate dont work
precio_leche['mes_pal'] = precio_leche['mes_pal'].str.strip().str.lower().map(month_dict).astype(str).str.zfill(2)
precio_leche['mes'] = pd.to_datetime(precio_leche['mes_pal'], format = '%m')

precio_leche['mes'] = precio_leche['mes'].apply(lambda x: x.month)
precio_leche['mes-ano'] = precio_leche.apply(lambda x: f'{x.mes}-{x.ano}', axis = 1)

precipitaciones['mes'] = precipitaciones.date.apply(lambda x: x.month)
precipitaciones['ano'] = precipitaciones.date.apply(lambda x: x.year)
precio_leche_pp = pd.merge(precio_leche, precipitaciones, on = ['mes', 'ano'], how = 'inner')
precio_leche_pp.drop('date', axis = 1, inplace = True)

banco_central_num['mes'] = banco_central_num['Periodo'].apply(lambda x: x.month)
banco_central_num['ano'] = banco_central_num['Periodo'].apply(lambda x: x.year)
precio_leche_pp_pib = pd.merge(precio_leche_pp, banco_central_num, on = ['mes', 'ano'], how = 'inner')
precio_leche_pp_pib.drop(['Periodo', 'Indice_de_ventas_comercio_real_no_durables_IVCM', 'mes-ano', 'mes_pal'], axis =1, inplace = True)


cc_cols = [x for x in precio_leche_pp_pib.columns if x not in ['ano', 'mes']]

precio_leche_pp_pib_shift3_mean = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).mean().shift(1)

precio_leche_pp_pib_shift3_mean.columns = [x+'_shift3_mean' for x in precio_leche_pp_pib_shift3_mean.columns]
                                                 
precio_leche_pp_pib_shift3_std = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).std().shift(1)

precio_leche_pp_pib_shift3_std.columns = [x+'_shift3_std' for x in precio_leche_pp_pib_shift3_std.columns] 

precio_leche_pp_pib_shift1 = precio_leche_pp_pib[cc_cols].shift(1)

precio_leche_pp_pib_shift1.columns = [x+'_mes_anterior' for x in precio_leche_pp_pib_shift1.columns]

precio_leche_pp_pib = pd.concat([precio_leche_pp_pib['Precio_leche'], precio_leche_pp_pib_shift3_mean, precio_leche_pp_pib_shift3_std, precio_leche_pp_pib_shift1], axis = 1) 
precio_leche_pp_pib = precio_leche_pp_pib.dropna(how = 'any', axis = 0)

""" save clean csv """
precio_leche_pp_pib.to_csv(precio_leche_output_path, index=False)