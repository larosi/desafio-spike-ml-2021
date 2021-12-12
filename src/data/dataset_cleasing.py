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
                           default="data/processed/merged.csv",
                           help='Path to save merged.csv dataset')
    
    my_parser.add_argument('--output_features',
                           type=str,
                           default="data/processed/features.csv",
                           help='Path to save features.csv to train a model')
    
    return my_parser.parse_args()

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

def convert_int(x):
    return int(x.replace('.', ''))

def cast_to_datetime(df, columns_to_cast = ['mes', 'date', 'Periodo']):
    month_dict = {'ene': 1, 'feb': 2, 'mar': 3,
                  'abr': 4, 'may': 5, 'jun': 6,
                  'jul': 7, 'ago': 8, 'sep': 9,
                  'oct': 10, 'nov': 11, 'dic': 12}

    for col_name in df.columns:
        if col_name in columns_to_cast:
            data_example = df[col_name].values[0]
            if isinstance(data_example, str):
                if len(data_example) > 10: # if longer than '%Y-%m-%d' format
                    df[col_name] = df[col_name].apply(lambda x: x[0:10])
                    df[col_name] = pd.to_datetime(df[col_name], format = '%Y-%m-%d', errors = 'coerce')
                elif len(data_example)==3: # if short month name format
                    df[col_name] = df[col_name].str.strip().str.lower().map(month_dict).astype(str).str.zfill(2)
                    df[col_name] = pd.to_datetime(df[col_name], format = '%m')
                else: # default '%Y-%m-%d' format
                    df[col_name] = pd.to_datetime(df[col_name], format = '%Y-%m-%d', errors = 'coerce')

    return df

def drop_undesired_columns(df, cols_to_keep):
    for col in df.columns:
        if col not in cols_to_keep:
            df.drop(col, axis = 1, inplace = True)

def compute_std_mean_shift(df, cols_to_ignore = ['ano', 'mes']):
    cc_cols = [x for x in df.columns if x not in cols_to_ignore]

    df_shift3_mean = df[cc_cols].rolling(window=3, min_periods=1).mean().shift(1)
    df_shift3_mean.columns = [x+'_shift3_mean' for x in df_shift3_mean.columns]    
                                        
    df_shift3_std = df[cc_cols].rolling(window=3, min_periods=1).std().shift(1)
    df_shift3_std.columns = [x+'_shift3_std' for x in df_shift3_std.columns] 
    
    df_shift1 = df[cc_cols].shift(1)
    df_shift1.columns = [x+'_mes_anterior' for x in df_shift1.columns]
    
    if 'Precio_leche' in df.columns:
        df = pd.concat([df['Precio_leche'], df_shift3_mean, df_shift3_std, df_shift1], axis = 1)
    else:
        df = pd.concat([df_shift3_mean, df_shift3_std, df_shift1], axis = 1)
    df = df.dropna(how = 'any', axis = 0)
    
    return df

""" Datos y limpieza de Datos"""
args = get_arguments()

precipitaciones_path = args.precipitaciones
banco_central_path = args.banco_central
precio_leche_path = args.precio_leche

merged_output_path = args.output_data
features_output_path = args.output_features

""" Precipitaciones """

precipitaciones = pd.read_csv(precipitaciones_path)
#precipitaciones = drop_dupicantes_and_nans(precipitaciones)
precipitaciones = cast_to_datetime(precipitaciones)
precipitaciones['mes'] = precipitaciones.date.apply(lambda x: x.month)
precipitaciones['ano'] = precipitaciones.date.apply(lambda x: x.year)
precipitaciones.drop('date', axis = 1, inplace = True)

""" Banco central """


banco_central = pd.read_csv(banco_central_path)

banco_central_columns = list(banco_central.columns)
cols_pib = [x for x in banco_central_columns if 'PIB' in x]
cols_imacec = [x for x in banco_central_columns if 'Imacec' in x]
col_iv = 'Indice_de_ventas_comercio_real_no_durables_IVCM'

cols_to_keep = cols_pib + cols_imacec + [col_iv, 'Periodo'] 
drop_undesired_columns(banco_central, cols_to_keep)

banco_central = cast_to_datetime(banco_central)

banco_central.drop_duplicates(subset = 'Periodo', inplace = True)
banco_central.dropna(axis=0, inplace=True)
#banco_central.dropna(subset=cols_pib+['Periodo'], inplace = True)



banco_central = banco_central.sort_values(by = 'Periodo', ascending = True)

for col in cols_pib:
    banco_central[col] = banco_central[col].apply(lambda x: convert_int(x))

for col in cols_imacec:
    banco_central[col] = banco_central[col].apply(lambda x: convert_int(x))
    
banco_central['num'] = banco_central[col_iv].apply(lambda x: to_100(x))

cols_to_keep = cols_pib + cols_imacec + ['num', 'mes', 'ano'] 

banco_central['mes'] = banco_central['Periodo'].apply(lambda x: x.month)
banco_central['ano'] = banco_central['Periodo'].apply(lambda x: x.year)

drop_undesired_columns(banco_central, cols_to_keep)

banco_central.reset_index(drop=True, inplace=True)

""" precio leche """

precio_leche = pd.read_csv(precio_leche_path)
precio_leche.rename(columns = {'Anio': 'ano', 'Mes': 'mes'}, inplace = True) # precio = nominal, sin iva en clp/litro

precio_leche = cast_to_datetime(precio_leche)
precio_leche['mes'] = precio_leche['mes'].apply(lambda x: x.month)

df_merged = pd.merge(precio_leche, precipitaciones, on = ['mes', 'ano'], how = 'inner')
df_merged = pd.merge(df_merged, banco_central, on = ['mes', 'ano'], how = 'inner')

df_shift = compute_std_mean_shift(df_merged)

""" save clean csv """

df_merged.to_csv(merged_output_path, index=False)
df_shift.to_csv(features_output_path, index=False)