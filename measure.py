import cv2
import numpy as np
import pygame
from skimage.metrics import structural_similarity as ssim
import os

class ShapeMeasure:
    def __init__(self):
        """Initialize the shape measurement class"""
        pass
        
    @staticmethod
    def surface_to_array(surface):
        """Convert a Pygame Surface to a numpy array"""
        try:
            # วิธีที่ 1: ใช้ pygame.surfarray (เร็วกว่า)
            arr = pygame.surfarray.array3d(surface)
            return arr.transpose(1, 0, 2)  # สลับ x, y เพื่อให้เป็นรูปแบบ OpenCV (height, width, channels)
        except Exception as e:
            print(f"Error using surfarray: {e}")
            # วิธีที่ 2: ใช้ pygame.image.tostring
            surface_str = pygame.image.tostring(surface, 'RGB')
            # Convert the raw pixel data to a numpy array
            img = np.frombuffer(surface_str, dtype=np.uint8).reshape(
                surface.get_height(), surface.get_width(), 3)
            return img
        
    @staticmethod
    def get_binary_image(surface, threshold=50, invert=True):
        """Convert a Pygame Surface to a binary image"""
        # Convert surface to numpy array
        img = ShapeMeasure.surface_to_array(surface)
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Apply thresholding to create binary image
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        # Median filtering to remove noise
        binary = cv2.medianBlur(binary, 5)
        # Invert the image (black background)
        if invert:
            binary = cv2.bitwise_not(binary)
        return binary
        
    @staticmethod
    def calculate_coverage(drawing_surface, template_surface):
        """
        Calculate the coverage ratio: intersection area / template area
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            template_surface: The Pygame surface containing the template
            
        Returns:
            float: Coverage percentage (0-100)
        """
        try:
            # Convert surfaces to binary images
            drawing_binary = ShapeMeasure.get_binary_image(drawing_surface, invert=False)
            template_binary = ShapeMeasure.get_binary_image(template_surface, threshold=120)
            
            # Ensure both images have the same dimensions
            if drawing_binary.shape != template_binary.shape:
                template_binary = cv2.resize(template_binary, 
                                           (drawing_binary.shape[1], drawing_binary.shape[0]))
                
            cv2.imwrite('debug_drawing_cov.png', drawing_binary)
            cv2.imwrite('debug_template_cov.png', template_binary)
            
            # คำนวณ intersection (พิกเซลที่อยู่ทั้งในภาพวาดและ template)
            intersection = cv2.bitwise_and(drawing_binary, template_binary)
            
            # คำนวณอัตราส่วน coverage
            template_area = np.count_nonzero(template_binary)
            drawing_area = np.count_nonzero(drawing_binary)
            
            print(f"Template area: {template_area} pixels")
            print(f"Drawing area: {drawing_area} pixels")
            
            if template_area == 0:  # ป้องกันการหารด้วยศูนย์
                print("Template area is zero")
                return 0.0
                
            intersection_area = np.count_nonzero(intersection)
            print(f"Intersection area: {intersection_area} pixels")
            
            coverage_ratio = (intersection_area / template_area) * 100
            print(f"Coverage: {coverage_ratio:.2f}%")
            
            return coverage_ratio
        except Exception as e:
            print(f"Error in calculate_coverage: {e}")
            return 0.0
        
    @staticmethod
    def calculate_out_of_bounds(drawing_surface, template_surface):
        """
        Calculate the out-of-bounds ratio: (drawing area - intersection) / drawing area
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            template_surface: The Pygame surface containing the template
            
        Returns:
            float: Out-of-bounds percentage (0-100)
        """
        try:
            # Convert surfaces to binary images
            drawing_binary = ShapeMeasure.get_binary_image(drawing_surface, invert=False)
            template_binary = ShapeMeasure.get_binary_image(template_surface, threshold=120)
            
            # Ensure both images have the same dimensions
            if drawing_binary.shape != template_binary.shape:
                template_binary = cv2.resize(template_binary, 
                                           (drawing_binary.shape[1], drawing_binary.shape[0]))
                
            
            cv2.imwrite('debug_drawing_ofb.png', drawing_binary)
            cv2.imwrite('debug_template_ofb.png', template_binary)
            
            # Calculate intersection
            intersection = cv2.bitwise_and(drawing_binary, template_binary)
            
            # Calculate out-of-bounds area (pixels in drawing but not in template)
            drawing_area = np.count_nonzero(drawing_binary)
            intersection_area = np.count_nonzero(intersection)
            out_of_bounds_area = drawing_area - intersection_area
            
            print(f"Out of bounds area: {out_of_bounds_area} pixels")
            
            # คำนวณอัตราส่วนเทียบกับพื้นที่วาดทั้งหมด
            if drawing_area == 0:  # ป้องกันการหารด้วยศูนย์
                return 0.0
                
            out_of_bounds_ratio = (out_of_bounds_area / drawing_area) * 100
            print(f"Out of bounds: {out_of_bounds_ratio:.2f}%")
            
            return out_of_bounds_ratio
        except Exception as e:
            print(f"Error in calculate_out_of_bounds: {e}")
            return 0.0
    
    @staticmethod
    def calculate_similarity(drawing_surface, template_surface):
        """
        Calculate the structural similarity between the drawing and template
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            template_surface: The Pygame surface containing the template
            
        Returns:
            float: Similarity score (0-100)
        """
        try:
            # Convert surfaces to binary images
            drawing_binary = ShapeMeasure.get_binary_image(drawing_surface, invert=False)
            template_binary = ShapeMeasure.get_binary_image(template_surface, threshold=120)
            
            # Ensure both images have the same dimensions
            if drawing_binary.shape != template_binary.shape:
                template_binary = cv2.resize(template_binary, 
                                          (drawing_binary.shape[1], drawing_binary.shape[0]))
                
            cv2.imwrite('debug_drawing_sim.png', drawing_binary)
            cv2.imwrite('debug_template_sim.png', template_binary)
            
            # Calculate structural SSIM similarity
            ssim_score, _ = ssim(drawing_binary, template_binary, full=True, data_range=255)
            ssim_similarity = max(0, ssim_score * 100)

            # Convert binary images to contours for matchShapes
            contours_drawing, _ = cv2.findContours(drawing_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_template, _ = cv2.findContours(template_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours_drawing and contours_template:
            # ใช้ contour ที่ใหญ่ที่สุด (assumption: รูปหลักอยู่ใน contour ที่ใหญ่ที่สุด)
                drawing_contour = max(contours_drawing, key=cv2.contourArea)
                template_contour = max(contours_template, key=cv2.contourArea)
                
                # Calculate shape similarity using matchShapes (0 = identical, higher = more different)
                shape_score = cv2.matchShapes(drawing_contour, template_contour, cv2.CONTOURS_MATCH_I1, 0.0)
                shape_similarity = max(0, 100 - (shape_score * 100))  # Scale to 0-100
            
                # Final similarity score (weighted)
                final_similarity = (ssim_similarity * 0.6) + (shape_similarity * 0.4)  # Adjust weights as needed
                print(f"SSIM similarity: {ssim_similarity:.2f}%")
                print(f"Shape similarity: {shape_similarity:.2f}%")
                print(f"Final similarity: {final_similarity:.2f}%")
                return final_similarity
            else:
                print("No contours found for similarity comparison")
                return 0.0
        except Exception as e:
            print(f"Error in calculate_similarity: {e}")
            return 0.0
    
    @staticmethod
    def calculate_accuracy(drawing_surface, binary_template_path):
        """
        Calculate the accuracy based on how well the drawing follows the template lines
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            binary_template_path: Path to the binary template image file
            
        Returns:
            float: Accuracy score (0-100)
        """
        try:
            import os
            
            # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
            if not os.path.exists(binary_template_path):
                print(f"Binary template not found: {binary_template_path}")
                
                # ลองค้นหาในตำแหน่งอื่น
                alt_paths = []
                basename = os.path.basename(binary_template_path)
                
                if 'assets/bin' in binary_template_path:
                    alt_paths.append(basename)  # ลองในโฟลเดอร์ปัจจุบัน
                    alt_paths.append(f"assets/{basename}")  # ลองในโฟลเดอร์ assets
                
                for path in alt_paths:
                    if os.path.exists(path):
                        print(f"Found binary template at: {path}")
                        binary_template_path = path
                        break
            
            # โหลด binary template
            binary_template = cv2.imread(binary_template_path, cv2.IMREAD_GRAYSCALE)
            if binary_template is None:
                print(f"Could not load binary template from {binary_template_path}")
                
                # สร้าง template ชั่วคราวถ้าไม่พบไฟล์
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_path = temp_file.name
                
                # สร้าง dummy template (เส้นขอบสี่เหลี่ยม)
                dummy_template = np.zeros((400, 400), dtype=np.uint8)
                cv2.rectangle(dummy_template, (50, 50), (350, 350), 255, 2)
                cv2.imwrite(temp_path, dummy_template)
                
                binary_template = dummy_template
                print(f"Created temporary template at: {temp_path}")
            
            # แปลง drawing surface เป็น numpy array
            drawing_img = ShapeMeasure.surface_to_array(drawing_surface)
            drawing_gray = cv2.cvtColor(drawing_img, cv2.COLOR_RGB2GRAY)
            _, drawing_binary = cv2.threshold(drawing_gray, 50, 255, cv2.THRESH_BINARY)
            
            # ปรับขนาด template ให้ตรงกับ drawing
            binary_template = cv2.resize(binary_template, 
                                       (drawing_binary.shape[1], drawing_binary.shape[0]))
            
            # ดีบัก: บันทึกรูปภาพเพื่อตรวจสอบ
            cv2.imwrite('debug_binary_drawing_acc.png', drawing_binary)
            cv2.imwrite('debug_binary_template_acc.png', binary_template)
            
            # สร้าง distance transform จาก template
            # นี่จะให้ค่าระยะห่างจากเส้น template ที่ใกล้ที่สุดสำหรับแต่ละพิกเซล
            dist_transform = cv2.distanceTransform(255 - binary_template, cv2.DIST_L2, 3)
            
            # หาค่าระยะห่างสูงสุด
            max_dist = np.max(dist_transform)
            print(f"Max distance in transform: {max_dist}")
            
            # ป้องกันการหารด้วยศูนย์
            if max_dist <= 0:
                return 0.0
            
            # หาพิกัดของพิกเซลที่วาด
            drawing_coords = np.where(drawing_binary > 0)
            
            if len(drawing_coords[0]) == 0:  # ไม่มีพิกเซลที่วาด
                return 0.0
            
            # คำนวณระยะห่างทั้งหมดสำหรับพิกเซลที่วาด
            total_dist = 0
            close_points = 0
            threshold_dist = max_dist * 0.1  # พิกเซลที่อยู่ภายใน 10% ของระยะห่างสูงสุดถือว่าอยู่บนเส้น
            
            for y, x in zip(drawing_coords[0], drawing_coords[1]):
                dist = dist_transform[y, x]
                total_dist += dist
                if dist < threshold_dist:
                    close_points += 1
            
            # คำนวณคะแนนความแม่นยำจากสองส่วน:
            # 1. สัดส่วนของพิกเซลที่วาดที่อยู่ใกล้เส้น template
            # 2. ระยะห่างเฉลี่ยจากเส้น template (ปรับเป็นคะแนน 0-100)
            
            point_ratio = close_points / len(drawing_coords[0])
            avg_dist = total_dist / len(drawing_coords[0])
            dist_score = 100 * (1 - min(avg_dist / max_dist, 1.0))
            
            # รวมทั้งสองคะแนนเข้าด้วยกัน
            accuracy = (point_ratio * 50) + (dist_score * 0.5)
            print(f"Accuracy: point_ratio={point_ratio:.2f}, dist_score={dist_score:.2f}, final={accuracy:.2f}%")
            
            return accuracy
        except Exception as e:
            print(f"Error in calculate_accuracy: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    @staticmethod
    def evaluate_drawing(drawing_surface, template_surface, binary_template_path=None):
        """
        Comprehensive evaluation of a drawing against a template
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            template_surface: The Pygame surface containing the template
            binary_template_path: Optional path to a pre-processed binary template
            
        Returns:
            dict: Dictionary containing all metrics
        """
        try:
            print("\n--- EVALUATING DRAWING ---")
            
            # Calculate basic metrics
            coverage = ShapeMeasure.calculate_coverage(drawing_surface, template_surface)
            out_of_bounds = ShapeMeasure.calculate_out_of_bounds(drawing_surface, template_surface)
            similarity = ShapeMeasure.calculate_similarity(drawing_surface, template_surface)
            
            # Calculate accuracy if binary template is provided
            accuracy = 0.0
            if binary_template_path:
                accuracy = ShapeMeasure.calculate_accuracy(drawing_surface, binary_template_path)
            
            # Combine metrics into overall score
            if binary_template_path:
                # Use all metrics including accuracy
                overall_score = (coverage * 0.3 + 
                               (100 - out_of_bounds) * 0.2 + 
                               similarity * 0.2 + 
                               accuracy * 0.3)
            else:
                # Use only basic metrics
                overall_score = (coverage * 0.4 + 
                               (100 - out_of_bounds) * 0.3 + 
                               similarity * 0.3)
            
            print(f"Overall score: {overall_score:.2f}%")
            print("--- EVALUATION COMPLETE ---\n")
            
            # Return all metrics as a dictionary
            return {
                "coverage": coverage,
                "out_of_bounds": out_of_bounds,
                "similarity": similarity,
                "accuracy": accuracy if binary_template_path else None,
                "overall_score": overall_score
            }
        except Exception as e:
            print(f"Error in evaluate_drawing: {e}")
            import traceback
            traceback.print_exc()
            
            # คืนค่าเริ่มต้นถ้าเกิดข้อผิดพลาด
            return {
                "coverage": 0.0,
                "out_of_bounds": 0.0,
                "similarity": 0.0,
                "accuracy": 0.0 if binary_template_path else None,
                "overall_score": 0.0
            }
    
    @staticmethod
    def load_binary_template(difficulty):
        """
        โหลด binary template ตามระดับความยาก
        
        Args:
            difficulty: ระดับความยาก ("Easy", "Normal", "Hard")
            
        Returns:
            str: เส้นทางไปยังไฟล์ binary template
        """
        difficulty = difficulty.lower()
        return f"assets/bin2/cookie_template_{difficulty}_bin.png"
    
    @staticmethod
    def get_visualization(drawing_surface, template_surface, binary_template_path=None):
        """
        Generate a visualization surface showing the evaluation results
        
        Args:
            drawing_surface: The Pygame surface containing the user's drawing
            template_surface: The Pygame surface containing the template
            binary_template_path: Optional path to a pre-processed binary template
            
        Returns:
            pygame.Surface: Surface with visualization
        """
        # Create a copy of the template surface
        template_width = template_surface.get_width()
        template_height = template_surface.get_height()
        
        # Create a new surface for visualization
        vis_surface = pygame.Surface((template_width, template_height), pygame.SRCALPHA)
        
        # Convert surfaces to binary images
        drawing_binary = ShapeMeasure.get_binary_image(drawing_surface, invert=False)
        template_binary = ShapeMeasure.get_binary_image(template_surface, threshold=120)
        
        # Resize if needed
        if drawing_binary.shape != (template_height, template_width):
            drawing_binary = cv2.resize(drawing_binary, (template_width, template_height))
        
        # Load binary template if provided
        binary_template = None
        if binary_template_path and os.path.exists(binary_template_path):
            binary_template = cv2.imread(binary_template_path, cv2.IMREAD_GRAYSCALE)
            if binary_template is not None:
                binary_template = cv2.resize(binary_template, (template_width, template_height))
        
        # Create colored visualization
        # - Green: Intersection (drawing on template)
        # - Red: Out of bounds (drawing outside template)
        # - Blue: Template outline
        
        # Convert numpy arrays to pygame surfaces
        if binary_template is not None:
            binary_surface = pygame.surfarray.make_surface(binary_template)
            vis_surface.blit(binary_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Calculate intersection
        intersection = cv2.bitwise_and(drawing_binary, template_binary)
        out_of_bounds_binary = cv2.subtract(drawing_binary, intersection)
        
        # Create colored surfaces
        green_surface = pygame.Surface((template_width, template_height), pygame.SRCALPHA)
        red_surface = pygame.Surface((template_width, template_height), pygame.SRCALPHA)
        
        # Set pixels
        intersection_coords = np.where(intersection > 0)
        for y, x in zip(intersection_coords[0], intersection_coords[1]):
            if 0 <= y < template_height and 0 <= x < template_width:
                green_surface.set_at((x, y), (0, 255, 0, 128))
        
        out_coords = np.where(out_of_bounds_binary > 0)
        for y, x in zip(out_coords[0], out_coords[1]):
            if 0 <= y < template_height and 0 <= x < template_width:
                red_surface.set_at((x, y), (255, 0, 0, 128))
        
        # Combine surfaces
        vis_surface.blit(green_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        vis_surface.blit(red_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        return vis_surface