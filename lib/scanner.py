import cv2
import time
import pyzbar.pyzbar as pyzbar
import numpy as np
import winsound

def beep(num_beeps, duration, interval):
    for i in range(num_beeps):
        winsound.Beep(frequency=600, duration=duration)
        time.sleep(interval)

def scan_qr_code(token):
    # Start webcam
    cap = cv2.VideoCapture(0)
    
    while True:
        prev_data = None
        while True:
            ret, frame = cap.read()

            # Convert to grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Increase brightness a bit
            frame = cv2.add(frame, np.array([100.0]))

            # Convert to binary
            frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Make it adaptive
            frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Decode the QR code and run the filament_data function
            if not ret:
                break
            decoded_objs = pyzbar.decode(frame, symbols=[pyzbar.ZBarSymbol.QRCODE])
            if len(decoded_objs) > 0:
                for obj in decoded_objs:
                    data = obj.data.decode("utf-8")
                    if data != prev_data:
                        prev_data = data
                        #data = token(data)
                        beep(1,140,0)

            
            # Change frame to rgb
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB) 

            # Draw a rectangle around the QR code
            for decoded_obj in decoded_objs:
                points = decoded_obj.polygon
                # If the points do not form a quad, find convex hull
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    hull = list(map(tuple, np.squeeze(hull)))
                else:
                    hull = points
                # Number of points in the convex hull
                n = len(hull)
                # Draw the convext hull
                for j in range(0, n):
                    cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 255, 0), 3)
           
            # Display the resulting frame
            cv2.imshow("frame", frame)

            # Press q to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        # Release the VideoCapture object and close all windows
        cap.release()
        cv2.destroyAllWindows()