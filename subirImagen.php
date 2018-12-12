<?php
 $imagen= $_POST['foto'];
 $url= "http://localhost:5550/cargar";//url de tu api

 $ch= curl_init($url);

 $arreglo=array();// meto en un arreglo la imagen en base64 para poder poner el encabezado dato
 $arreglo['dato']=$imagen;
 $json= json_encode($arreglo);//convierto a json

 curl_setopt($ch, CURLOPT_POST,1);
 curl_setopt($ch,CURLOPT_POSTFIELDS,$json);
 curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json')); //especifico que mandare un archivo json
 $result = curl_exec($ch);
 curl_close($ch);
 $respuesta = file_get_contents("imagen/respuesta.json");//leo json con respuesta 
 $json= json_decode($respuesta,true); //convierto el json a cadena
  echo $json; //la retorno a la app 
?>
