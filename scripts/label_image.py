# -*- coding: utf-8 -*-
#==============================================================================
#   Este script muestra el nivel de coincidencia de la imagen basado en
#    el entrenamiento de clasificación del programa.
#==============================================================================
#
#==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import requests
import json
import argparse
import sys
import time
#import os
import numpy as np
import tensorflow as tf

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
#Descargar imagen y renombrarla
#url_imagen = "http://localhost/app/imagen/descargar.php"
#url_imagen = "http://dialis.000webhostApp.com/imagen/descargar.php"
#nombre_imagen = "imagen2.jpg"
#imagen = requests.get(url_imagen).content
#with open(nombre_imagen, 'wb') as handler:
#  handler.write(imagen)


def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
        input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

def calculo(file_name):
  model_file = "../tf_files/retrained_graph.pb"
  label_file = "../tf_files/retrained_labels.txt"
  input_height = 224
  input_width = 224
  input_mean = 128
  input_std = 128
  input_layer = "input"
  output_layer = "final_result"

  graph = load_graph(model_file)
  t = read_tensor_from_image_file(file_name,
                                  input_height=input_height,
                                  input_width=input_width,
                                  input_mean=input_mean,
                                  input_std=input_std)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name);
  output_operation = graph.get_operation_by_name(output_name);

  file = open('/var/www/html/imagen/respuesta.json','w')
  #read_file = file.write('Hola')
  #url_datos = "https://dialis.000webhostapp.com/respuesta.php?rest="
  #url_datos = "http://localhost/app/respuesta.php?rest="
  with tf.Session(graph=graph) as sess:
    start = time.time()
    results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
    end=time.time()
  resultado = np.squeeze(results)

  arreglo = resultado.argsort()[-5:][::-1]
  etiqueta = load_labels(label_file)
  print("================================================================================")
  print("                     Detección de Roya en planta de café             ")
  print("================================================================================")

  print('Tiempo de evaluación (1 imagen): {:.3f}s\n'.format(end-start))
  template = "{}{:0.5f}"
  for i in arreglo:
    print(template.format(etiqueta[i],resultado[i]))
    #file.write(template.format("{"+etiqueta[i]+"}"+","+"{",resultado[i])+"} \n")
    #file.write(template.format("",+resultado[0])+"\n")
    #if(resultado[0]>0.5)
    temporal=resultado[0]
    flotante = (float(temporal)*100)
    redondo = str(int(round(flotante,0)))

  file.write('"'+str(redondo)+'"'+"\n")
  print('"'+str(redondo)+'"')
    
  
  return redondo

if __name__ == "__main__":
  #file_name = "tf_files/flower_photos/daisy/3475870145_685a19116d.jpg"
  model_file = "tf_files/retrained_graph.pb"
  label_file = "tf_files/retrained_labels.txt"
  input_height = 224
  input_width = 224
  input_mean = 128
  input_std = 128
  input_layer = "input"
  output_layer = "final_result"

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="imagen a procesar")
  args = parser.parse_args()

  if args.image:
    file_name = args.image

  graph = load_graph(model_file)
  t = read_tensor_from_image_file(file_name,
                                  input_height=input_height,
                                  input_width=input_width,
                                  input_mean=input_mean,
                                  input_std=input_std)

  input_name = "import/" + input_layer
  output_name = "import/" + output_layer
  input_operation = graph.get_operation_by_name(input_name);
  output_operation = graph.get_operation_by_name(output_name);

  file = open('/var/www/html/imagen/respuesta.json','w')
  #read_file = file.write('Hola')
  #url_datos = "https://dialis.000webhostapp.com/respuesta.php?rest="
  url_datos = "http://localhost/app/respuesta.php?rest="
  with tf.Session(graph=graph) as sess:
    start = time.time()
    results = sess.run(output_operation.outputs[0],
                      {input_operation.outputs[0]: t})
    end=time.time()
  resultado = np.squeeze(results)

  arreglo = resultado.argsort()[-5:][::-1]
  etiqueta = load_labels(label_file)
  print("================================================================================")
  print("                     Detección de Roya en planta de café             ")
  print("================================================================================")

  print('Tiempo de evaluación (1 imagen): {:.3f}s\n'.format(end-start))
  template = "{}{:0.5f}"
  for i in arreglo:
    print(template.format(etiqueta[i],resultado[i]))
    #file.write(template.format("{"+etiqueta[i]+"}"+","+"{",resultado[i])+"} \n")
    #file.write(template.format("",+resultado[0])+"\n")
    #if(resultado[0]>0.5)
    temporal=resultado[0]
    flotante = (float(temporal)*100)
    redondo = int(round(flotante,0))
    
  
  print('"'+str(redondo)+'"'+"\n")
  resp = requests.get(url_datos+ str(redondo))
  data = resp.json
  file.write('"'+str(redondo)+'"')
  file.close()
