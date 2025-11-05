import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import keyboard
import os
from flask import Flask, Response, render_template_string, send_from_directory

app = Flask(__name__)

#SSD face detection model (Caffe,32bit)
PROTO_PATH = "/root/deploy.prototxt"
MODEL_PATH = "/root/res10_300x300_ssd_iter_140000.caffemodel"

net = cv2.dnn.readNetFromCaffe(PROTO_PATH, MODEL_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

#Semantic segmentation model (TFLite,32bit)
SEG_MODEL_PATH = "/root/selfie_multiclass_256x256.tflite"
seg_interpreter = tflite.Interpreter(model_path=SEG_MODEL_PATH)
seg_interpreter.allocate_tensors()
seg_input = seg_interpreter.get_input_details()
seg_output = seg_interpreter.get_output_details()

#Kayit klasoru
SAVE_DIR = "/root/segments"
os.makedirs(SAVE_DIR, exist_ok=True)
segment_counter = 1

#Kamera ayarlari
cap = cv2.VideoCapture("/dev/video5", cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

#Segmentasyon fonksiyonu
def segment_face(face_roi):
    inp = cv2.resize(face_roi, (256, 256))
    inp = inp.astype(np.float32) / 255.0
    inp = np.expand_dims(inp, axis=0)
    seg_interpreter.set_tensor(seg_input[0]['index'], inp)
    seg_interpreter.invoke()

    mask = seg_interpreter.get_tensor(seg_output[0]['index'])[0]
    mask = np.argmax(mask, axis=-1).astype(np.uint8)
    mask = cv2.resize(mask, (face_roi.shape[1], face_roi.shape[0]), interpolation=cv2.INTER_NEAREST)

    # Yüz/cilt siniflari(1 Yada 2)
    face_mask = np.where((mask == 1) | (mask == 2), 255, 0).astype(np.uint8)
    colored_mask = cv2.applyColorMap(face_mask, cv2.COLORMAP_JET)
    blended = cv2.addWeighted(face_roi, 0.6, colored_mask, 0.4, 0)
    return blended

#Yüz tespiti fonksiyonu
def detect_faces(frame):
    global segment_counter
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.998:
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (startX, startY, endX, endY) = box.astype("int")

            face_roi = frame[startY:endY, startX:endX].copy()

            #'S' tusuna basilmissa segmentasyonu yap ve kaydet
            if keyboard.is_pressed("s") and face_roi.size > 0:
                try:
                    seg_result = segment_face(face_roi)
                    save_path = os.path.join(SAVE_DIR, f"segment_{segment_counter:03d}.jpg")
                    cv2.imwrite(save_path, seg_result)
                    print(f"Segment kaydedildi: {save_path}")
                    segment_counter += 1
                except Exception as e:
                    print("Segmentasyon hatası:", e)

            # Cerceve cizme
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 255), 2)
            cv2.putText(frame, f"Face: {confidence*100:.1f}%", (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    return frame

#Flask video akisi ayarlari
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = detect_faces(frame)
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#Galeri yonlendirme
@app.route('/gallery')
def gallery():
    files = sorted(os.listdir(SAVE_DIR))
    images_html = "".join([
        f"<div style='display:inline-block;margin:5px;'><img src='/segments/{f}' width='240'><p>{f}</p></div>"
        for f in files if f.lower().endswith(".jpg")
    ])
    html = f"""
    <html>
        <head><title>Segmentasyon Galerisi</title></head>
        <body style='background:#111;color:#eee;text-align:center;'>
            <h2>Segmentasyon Sonuçları</h2>
            <a href='/'>Canlı Yayına Dön</a><br><br>
            {images_html if images_html else "<p>Henüz segment kaydı yok.</p>"}
        </body>
    </html>
    """
    return render_template_string(html)

@app.route('/segments/<path:filename>')
def serve_segments(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == "__main__":
    print("SD Face Detection + Semantic Segmentation Sunucusu Baslatıldı")
    print("Canlı yayın icin: http://<TINKER_IP>:5000")
    print("Galeriye erismek ici: http://<TINKER_IP>:5000/gallery")
    print(" 'S' tuşuna basınca segment edilmiş yüz kaydedilir.")
    app.run(host="0.0.0.0", port=5000, threaded=True)

