# Relatório Final SMU - Detecção facial com RTSP e OpenCV

```sh
Autores: Bruno A. de Pinho e Jessica de Souza
```

O objetivo deste trabalho é realizar a detecção facial em tempo real a partir de uma câmera IP utilizando algoritmos de visão computacional e o uso de RTSP para a transmissão da mídia.

## Resumo do cenário:
Foi realizada uma transmissão de vídeo via streaming, utilizando o protocolo RTSP para negociação e transmissão. O primeiro streaming foi a imagem de captura da câmera VIP-S4000, da Intelbras. Esta streaming foi oferecida através de uma URI RTSP para o servidor de processamento. O servidor de processamento realizou a análise da imagem, identificando faces e inserindo a censura de rostos, utilizando visão computacional. Por fim, a imagem processada foi retornada ao cliente através de uma segunda URI RTSP. A imagem abaixo exemplifica o cenário utilizado.
 

[![CenarioRede](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/cenario.png)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/cenario.png) 
 
## Comunicação entre cliente e servidor:

A câmera IP usada neste trabalho apresentou alterações de seu IP de acordo com a rede em que estava conectada. Para que fosse simplificada a atualização da URI da câmera para o servidor, realizamos uma comunicação via sockets entre cliente e servidor. No lado cliente, é enviado para o servidor por meio de uma string a URI para acesso RTSP da câmera, que possui a seguinte estrutura:

```sh
rtsp://admin:admin@IP_DA_CAMERA:554/cam/realmonitor?channel=1&subtype=0
```
O servidor recebe esta URI, realiza o acesso à câmera via streaming e faz os devidos processamentos. Ao final, o servidor envia uma URI de volta ao cliente via socket, com a seguinte estrutura:

```sh
IP:PORTA_RTSP/timestamp_da_requisição
```
O timestamp é uma forma de a cada streaming haver um identificador único, que seria o momento da requisição.

## Implementação do algoritmo em Python:

```sh
Implementação baseada em: https://github.com/superdump/pyrtsp, onde realizamos a instalação de todas as extensões recomendadas para o funcionamento do programa.
```

Existem duas classes principais em nossa implementação, o SensorFactory e o GstServer. Foi utilizado o Gstreamer junto com RTSP para que fosse realizada a captura em tempo real e processamento da imagem. Embora foi definido inicialmente que iríamos processar a imagem e trabalhar com MJPEG, na implementação acabamos trabalhando com H.264 pois as documentações da parte de codificação da stream não foram suficientes para que conseguíssemos usar o MJPEG. Isso acarretou em um peso de processamento muito grande para a captura da imagem da câmera (que possuía resolução de 1280x720), levando a demora e atrasos na visualização da imagem processada no lado do cliente. Mesmo realizando a troca da câmera para a webcam do servidor (resolução de 640x480), houve uma diminuição neste atraso, porém o sistema ainda encontrava-se travado.

Na classe SensorFactory é implementado os seguintes itens:
- Recebimento da URI da câmera do lado cliente;
- Envio da URI com a stream processada para o cliente;
- Processamento da stream para a detecção facial e censura da região do rosto e retorno da imagem em escala RGB;
- Geração do buffer para envio da imagem por RTSP

Na classe GstServer é realizada a chamada da classe SensorFactory e envido ....... [CONTINUAR AQUI]


## O algoritmo de detecção facial:
[CONTINUAR A partir DAQUI]


# [estrutura] O relatório do projeto final deve contemplar os 4 componentes básicos e, como bônus, os 2 adicionais:

## Sinalização:
Feita através do RTSP

[![CenarioRtsp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtsp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtsp.PNG) 

## Negociação de mídia:
Feito através do SDP

[![Cenariosdp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-sdp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-sdp.PNG) 


## Escolha de caminho;

## Transporte de Mídia;
Utilizou o servidor Gstreamer (correto??)


(Opcional) Qualidade de serviço;
(Opcional) Segurança.

Link referência relatório: https://boidacarapreta.github.io/smu20191/projeto_final.html
Link do doc no drive: https://docs.google.com/document/d/1l3-EUnozrC__X8u3-rP3zjWsLCE4jsb9OfjaAeeTzh0/edit
