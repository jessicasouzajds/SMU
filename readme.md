# Relatório Final SMU - Detecção facial com RTSP e OpenCV

```sh
Autores: Bruno A. de Pinho e Jessica de Souza
```

O objetivo deste trabalho é realizar a detecção facial em tempo real a partir de uma câmera IP utilizando algoritmos de visão computacional e o uso de RTSP para a transmissão da mídia. O arquivo com captura dos pacote utilizados nesse trabalho pode ser encontrado [aqui](https://drive.google.com/open?id=1fjvjj6kFI97BoT07Brg2wAK1wqSzFUsZ).

## - Resumo do cenário:
Foi realizada uma transmissão de vídeo via streaming, utilizando o protocolo RTSP para negociação e transmissão. O primeiro streaming foi a imagem de captura da câmera VIP-S4000, da Intelbras. Esta streaming foi oferecida através de uma URI RTSP para o servidor de processamento. O servidor de processamento realizou a análise da imagem, identificando faces e inserindo a censura de rostos, utilizando visão computacional. Por fim, a imagem processada foi retornada ao cliente através de uma segunda URI RTSP. A imagem abaixo exemplifica o cenário utilizado.
 

[![CenarioRede](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/cenario.png)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/cenario.png) 
 
## - Comunicação entre cliente e servidor:

A câmera IP usada neste trabalho apresentou alterações de seu IP de acordo com a rede em que estava conectada. Para que fosse simplificada a atualização da URI da câmera para o servidor, realizamos uma comunicação via sockets entre cliente e servidor. No lado cliente, é enviado para o servidor por meio de uma string a URI para acesso RTSP da câmera, que possui a seguinte estrutura:

```sh
rtsp://admin:admin@IP_DA_CAMERA:554/cam/realmonitor?channel=1&subtype=0
```
O servidor recebe esta URI, realiza o acesso à câmera via streaming e faz os devidos processamentos. Ao final, o servidor envia uma URI de volta ao cliente via socket, com a seguinte estrutura:

```sh
IP:PORTA_RTSP/timestamp_da_requisição
```
O timestamp é uma forma de a cada streaming haver um identificador único, que seria o momento da requisição.

## - Implementação do algoritmo em Python:

```sh
Implementação baseada em: https://github.com/superdump/pyrtsp.
Realizamos a instalação de todas as extensões recomendadas para o funcionamento do programa.
```

Existem duas classes principais em nossa implementação, o SensorFactory e o GstServer. Foi utilizado o Gstreamer junto com RTSP para que fosse realizada a captura em tempo real e processamento da imagem. Embora foi definido inicialmente que iríamos processar a imagem e trabalhar com MJPEG, na implementação acabamos trabalhando com H.264 pois as documentações da parte de codificação da stream não foram suficientes para que conseguíssemos usar o MJPEG. Isso acarretou em um peso de processamento muito grande para a captura da imagem da câmera (que possuía resolução de 1280x720), levando a demora e atrasos na visualização da imagem processada no lado do cliente. Mesmo realizando a troca da câmera para a webcam do servidor (resolução de 640x480), houve uma diminuição neste atraso, porém o sistema ainda encontrava-se travado.

Na classe SensorFactory é implementado os seguintes itens:
- Recebimento da URI da câmera do lado cliente;
- Envio da URI com a stream processada para o cliente;
- Processamento da stream para a detecção facial e censura da região do rosto e retorno da imagem em escala RGB;

Na classe GstServer é realizada a preparação do servidor RTSP, preparando a mídia para transmissão após o processamento.


## - O algoritmo de detecção facial:

Para a detecção de facial foi utilizado o método Haar Cascade, o qual é um método eficaz de detecção de objetos proposto por Paul Viola e Michael Jones. É uma abordagem baseada em Machine Learning em que uma função cascade é treinada com diversas imagens positivas e negativas, a qual é então usada para detectar objetos em outras imagens.

A função implementada usa parâmetros prontos, os quais se encontram em um arquivo xml. O modelo utilizado foi treinado para faces frontais podendo ter problemas caso o rosto a ser detectado esteja virado em ângulo. Devido a constrições temporais foi utilizado o código como base para a implementação.

Para a omissão da face detectada, uma vez detectado o rosto foi realizada uma redução de resolução para 4x4, em seguida foi aumentada a resolução de volta para a original e assim tendo como resultado uma área pixelada devido à perda de informação. A área da face é então sobrescrita com a imagem pixelada, fazendo com que se torne impossivel recuperar a imagem original. A figura a seguir mostra o funcionamento do algoritmo de detecção facial e pixelização.

[![facedetect](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/face-detect.png)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/face-detect.png) 


## - Mídias:

A parte a seguir explora toda a parte de tráfego de dados por detrás da aplicação, detalhando as partes de sinalização, negociação, escolha de caminho e transporte de mídia.

### 1. Sinalização:

#### a. Requisições: 

A figura a seguir mostra no wireshark o agrupamento das requisições existentes na nossa transmissão, obtidas através da opção Telephony>RTSP>Packet Counter. As requisições foram: SETUP, PLAY, GET_PARAMETER, DESCRIBE, OPTIONS. O pacote de setup inicia a sessão RTSP, o pacote de play inicia a transmissão de dados na stream, o pacote de teardown faz com que a sessão RTSP deixe de existir e o describe especifica a apresentação do objeto de mídia. A figura a seguir mostra o agrupamento das mensagens RTSP, com a contagem de cada tipo de pacote gerado. 

[![Rtsp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtspp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtspp.PNG) 

#### b. Mensagens de Requisição e Respostas: 

A figura a seguir mostra fragmentos de mensagens RTSP com suas respectivas respostas. Houve um problema no início da streaming, onde não foi possível se conectar com a câmera, retornando um "service unavailable", mas logo em seguida reconfiguramos o IP da câmera e conseguimos sucesso na transmissão.

[![msg](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/mensagens-rtsp.png)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/mensagens-rtsp.png) 

A figura a seguir mostra o detalhamento da mensagem, na parte "real time streaming protocol", no wireshark.

[![CenarioRtsp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtsp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtsp.PNG) 


#### c.Transações e Diálogos:
A Figura a seguir mostra fragmentos da sequência para transações e diálogos. Note que para cada tipo de mensagem (ex. setup, play), há um número de sequência CSEQ que é igual para requisição e resposta, e é incrementado para a próxima mensagem.

[![detRtsp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/det-rtsp.png)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/det-rtsp.png) 

### 2. Negociação de mídia:

#### a. Tipos de mídia:
Para esse projeto foi utilizado como dados video e texto. O texto foi utlizado entre o cliente e servidor para a identificação das uri's RSTP com o streaming de video. O cliente envia uma mensagem de texto com a uri da streaming a ser censurada e o servidor responde com uma uri RSTP da streaming com as imagens já processadas e com censura de rosto. As streamings RSTP carregam apenas video, não contendo áudio.

#### b. Codecs: 
Foram utilizados dois codecs no projeto. O primeiro é o MJPG (Motion JPG) o que é proveniente da câmera capturando as imagens. Esse formato foi utilizado pois facilita o processamento das imagens, já que cada frame é uma imagen JPG. O segundo codec foi o H.264 o qual foi utilizado para transmissão da stream pós processamento. Apesar da qualidade de definição, o uso deste codec tornou a nossa transmissão pesada e com alta latência (apesar de o wireshark não ter conseguido mensurar, foi nítido o atraso para o carregamento da stream no lado cliente).

Os tipos de mídia e codecs podem ser vistos nos pacotes SDP (que descrevem a sessão em curso), note na figura a seguir que em vermelho estão destacadas estas informações obtidas no pacote capturado no wireshark.

[![Cenariosdp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-sdp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-sdp.PNG) 



### 3. Escolha de caminho;

#### a. Protocolos usados:
Durante a analise dos pacotes no wireshark não foram encontrados os pacotes com a troca de rotas. Também pode ser observado que embora a transmissão dos pacotes RTSP no servidor ocorram na interface 191.36.14.78, mesma rede da camera conforme selecionado no programa desenvolvido, a transmissão da midia ocorre na interface 191.36.11.76 que se encontram na mesma sub rede do cliente


### 4. Transporte de Mídia:

#### a. Protocolos usados: 
Para o transporte da mídia foi utilizado o protocolo RTP (Real time protocol, RFC 3550), que faz a transmissão de mídia em serviços de rede multicast e unicast. A figura a seguir mostra os pacotes RTP sendo transmitidos no Wireshark.

[![rtp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtp.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtp.PNG) 

#### b. Mecanismos de controle e monitoramento de entrega: quais os protocolos ou serviços de acompanhamento de:
- Latência;
-  Jitter; 
- Descarte de mensagem;

O próprio Wireshark possui ferramentas de análise de pacotes RTP, porém não foi possível executar as streams pois a configuração da gravação do RTP no lado do cliente não tornou possível visualizar a stream. No wireshark é possível verificar o total de pacotes transmitidos por stream, o total de pacotes perdidos e o valor delta calculado (que utiliza o marker para fazer os cálculos). Podemos observar que até o valor do marker, a largura de banda do pacote vai aumentando. O timestamp é a variável que é utilizada para o cálculo dos mecanismos de controle. Se o cliente e o servidor estivessem no mesmo host seria possível ter realizado os cálculos da forma correta.

As figuras a seguir mostram a ferramenta de análise de pacotes RTP, porém a latência dos pacotes nos pareceu estar calculada de forma incorreta, pois houve uma alta latência e no software este campo apresentou valores zerados.


[![rtp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtp1.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtp.PNG) 

   
[![rtp](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/wire-rtp2.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/rtp.PNG) 



### 5. Qualidade de serviço:

Para a qualidade de serviço, podemos observar no wireshark o uso do protocolo RTCP, que realiza as medições de atraso de jitter, conforme mostra a figura a seguir.

[![qos](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/qos.PNG)](https://github.com/jessicasouzajds/SMU/blob/face_detect/Images/qos.PNG) 


(Opcional) Segurança.

Link referência relatório: https://boidacarapreta.github.io/smu20191/projeto_final.html
Link do doc no drive: https://docs.google.com/document/d/1l3-EUnozrC__X8u3-rP3zjWsLCE4jsb9OfjaAeeTzh0/edit
