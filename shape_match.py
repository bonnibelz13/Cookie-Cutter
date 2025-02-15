# shape_match.py

import cv2

# def match_shapes(template_path, drawing):
#     """
#     เปรียบเทียบรูปทรงที่ผู้เล่นวาดกับรูปทรงต้นแบบ
#     """
#     template = cv2.imread(template_path, 0)
#     template = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)[1]
#     contours_template, _ = cv2.findContours(template, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     drawing_gray = cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY)
#     drawing_gray = cv2.threshold(drawing_gray, 127, 255, cv2.THRESH_BINARY)[1]
#     contours_drawing, _ = cv2.findContours(drawing_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     if contours_template and contours_drawing:
#         score = cv2.matchShapes(contours_template[0], contours_drawing[0], cv2.CONTOURS_MATCH_I1, 0.0)
#         return score
#     return 1.0  # คืนค่าสูงสุดหากไม่พบ contours