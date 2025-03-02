#accuracy.py
import cv2
import numpy as np

def get_cookie_contour(image, margin_size=0):
    """
    ดึง contour ของคุกกี้และเพิ่ม margin ถ้ากำหนดไว้
    """
    # แปลงเป็นภาพสีเทา
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ปรับความคมชัดด้วย Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # ใช้ Canny edge detection เพื่อเน้นขอบ
    edges = cv2.Canny(blurred, 50, 150)
    
    # หา contours จากขอบที่ได้
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # หากพบหลาย contours เลือกอันที่มีขนาดใหญ่ที่สุด (สมมติว่าคุกกี้ใหญ่สุด)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        if margin_size > 0:
            # ขยายขอบเขตโดยใช้ dilation
            mask = np.zeros_like(edges)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            kernel = np.ones((margin_size, margin_size), np.uint8)
            dilated = cv2.dilate(mask, kernel, iterations=1)
            
            # หา contours ใหม่หลังจาก dilation
            dilated_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if dilated_contours:
                return max(dilated_contours, key=cv2.contourArea)
        
        return largest_contour
    return None

def compute_accuracy(drawing_layer, cookie_image, margin_size=0):
    """
    คำนวณความแม่นยำของรูปวาดเทียบกับคุกกี้ โดยเพิ่ม margin ถ้ากำหนดไว้
    """
    # ดึงขอบคุกกี้พร้อม margin
    cookie_contour = get_cookie_contour(cookie_image, margin_size)
    if cookie_contour is None:
        return 0.0  # ถ้าหาขอบคุกกี้ไม่เจอ คืนค่าความแม่นยำเป็น 0
    
    # แปลงรูปวาดเป็นภาพไบนารี
    drawing_gray = cv2.cvtColor(drawing_layer, cv2.COLOR_BGR2GRAY)
    _, drawing_thresh = cv2.threshold(drawing_gray, 127, 255, cv2.THRESH_BINARY)
    
    # หา contours ของรูปวาด
    drawing_contours, _ = cv2.findContours(drawing_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not drawing_contours:
        return 0.0  # ถ้าไม่มีเส้นวาด คืนค่าความแม่นยำเป็น 0
    
    # เลือก contour ที่ใหญ่ที่สุดสำหรับเส้นวาด (ในกรณีที่มีหลายเส้น)
    drawing_contour = max(drawing_contours, key=cv2.contourArea)
    
    # ใช้ matchShapes เพื่อเปรียบเทียบ
    score = cv2.matchShapes(cookie_contour, drawing_contour, cv2.CONTOURS_MATCH_I1, 0.0)
    
    # แปลงคะแนนเป็นเปอร์เซ็นต์: คะแนนยิ่งต่ำ ความแม่นยำยิ่งสูง
    accuracy = max(0.0, 100.0 - score * 100)
    
    return accuracy
def get_rotated_points(points, angle):
    # ตัวอย่างโค้ด
    rotation_matrix = cv2.getRotationMatrix2D((0, 0), angle, 1)
    rotated_points = [cv2.transform(np.array([point]), rotation_matrix)[0][0] for point in points]
    return rotated_points
