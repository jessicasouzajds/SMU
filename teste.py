import cv2
import gi 
import numpy as np
import socket
from datetime import datetime
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0') 
from gi.repository import Gst, GstRtspServer, GObject

class SensorFactory(GstRtspServer.RTSPMediaFactory):
  def __init__(self, **properties): 
    super(SensorFactory, self).__init__(**properties) 
    #self.cap = cv2.VideoCapture(0) # webcam do computador
    self.ip = "191.36.14.78" # interface a ser utilizada
    self.port = 5556 # porta para receber a uri do cliente
    self.conn = self.recv_uri() # recebe a uri do cliente
    self.uri = self.conn[0] # string com uri recebida
    self.cap = cv2.VideoCapture(self.uri.decode('utf-8')) # captura imagens da uri
    self.number_frames = 0 
    self.fps = 30 # frames por segundo
    self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds 
    # string com os argumentos a serem passados para o GStreamer
    self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                         'caps=video/x-raw,format=BGR,width=640,height=480,framerate={}/1 ' \
                         '! videoconvert ! video/x-raw,format=I420 ' \
                         '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                         '! rtph264pay config-interval=1 name=pay0 pt=96'.format(self.fps) 
  
    #arquivo com os parametros do Haar Cascade
    cascPath = "haarcascade_frontalface_default.xml"

    # Create the haar cascade
    self.faceCascade = cv2.CascadeClassifier(cascPath)

  def recv_uri(self):
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_STREAM) # TCP
        sock.bind((self.ip, self.port))
        sock.listen(1)
        data, addr = sock.accept()
        uri = data.recv(1024) # espera a uri do cliente
        return (uri, sock, data)

  def send_uri(self, sock, data, media_id):
        msg = "rtsp://"+self.ip+":"+"8554"+ media_id # monta a uri da streaming censurada
        data.send(msg.encode()) # envia a uri para o cliente
        sock.close()

  def censored(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        width, height, _ = image.shape

        x = np.arange(height*width)
        x = x.reshape((width,height))
        mask = np.ones_like(x)



        # Desired "pixelated" size
        wi, he = (4, 4)
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            crop_img = gray[y:y+h,x:x+w]
            # Resize input to "pixelated" size
            temp = cv2.resize(crop_img, (wi, he), interpolation=cv2.INTER_LINEAR)

            # Initialize output image
            output = cv2.resize(temp, (w, h),      interpolation=cv2.INTER_NEAREST)
            # substitui a area da face com a imagem pixelada
            image[y:y+h,x:x+w,0] = output
            image[y:y+h,x:x+w,1] = output
            image[y:y+h,x:x+w,2] = output
        
        return image
        
        
  def on_need_data(self, src, lenght):
    if self.cap.isOpened():
      ret, frame = self.cap.read() # captura uma imagem
      if ret:
        image = self.censored(frame) # detecta e censura o rosto
        data = image.tostring()  # converte a imagem para uma string
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = self.duration
        timestamp = self.number_frames * self.duration
        buf.pts = buf.dts = int(timestamp)
        buf.offset = timestamp
        self.number_frames += 1
        retval = src.emit('push-buffer', buf) 

        print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames, self.duration, self.duration / Gst.SECOND)) 

        if retval != Gst.FlowReturn.OK: 
          print(retval) 

  def do_create_element(self, url): 
    return Gst.parse_launch(self.launch_string) 

  def do_configure(self, rtsp_media): 
    self.number_frames = 0 
    appsrc = rtsp_media.get_element().get_child_by_name('source') 
    appsrc.connect('need-data', self.on_need_data) 


class GstServer(GstRtspServer.RTSPServer): 
  def __init__(self, **properties): 
    super(GstServer, self).__init__(**properties) 
    self.factory = SensorFactory() 
    self.factory.set_shared(True)
    self.media_id = "/" + str(datetime.timestamp(datetime.now())) # cria um id para stream
    self.get_mount_points().add_factory(self.media_id, self.factory) # cria a stream
    self.factory.send_uri(self.factory.conn[1], self.factory.conn[2], self.media_id) # envia a uri da stream com a 
    #imagem processada para o cliente
    self.attach(None) 


# inicializa o servidor
GObject.threads_init() 
Gst.init(None) 

server = GstServer() 
server.set_address(server.factory.ip)
loop = GObject.MainLoop() 
loop.run()
