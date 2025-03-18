import cv2
import numpy as np
import time
import os

class VideoRecorder:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
        
        # Get camera properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = 30
        
        # Initialize state variables
        self.recording = False
        self.output = None
        self.start_time = 0
        self.filter_mode = 0  # 0: No filter, 1: Grayscale, 2: Sepia, 3: Edge detection
        self.flip_mode = 0  # 0: No flip, 1: Horizontal, 2: Vertical
        
        # Create output directory if it doesn't exist
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
    
    def start_recording(self):
        """Start recording video to a file"""
        if self.recording:
            return
        
        # Create filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/video_{timestamp}.mp4"
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec
        self.output = cv2.VideoWriter(filename, fourcc, self.fps, (self.frame_width, self.frame_height))
        
        if not self.output.isOpened():
            raise Exception("Could not create output video file")
        
        self.recording = True
        self.start_time = time.time()
    
    def stop_recording(self):
        """Stop recording video"""
        if not self.recording:
            return
        
        self.recording = False
        self.output.release()
        self.output = None
    
    def apply_filter(self, frame):
        """Apply visual filter to frame based on current filter_mode"""
        if self.filter_mode == 0:  # No filter
            return frame
        elif self.filter_mode == 1:  # Grayscale
            return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        elif self.filter_mode == 2:  # Sepia
            kernel = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
            sepia = cv2.transform(frame, kernel)
            return np.clip(sepia, 0, 255).astype(np.uint8)
        elif self.filter_mode == 3:  # Edge detection
            edges = cv2.Canny(frame, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def apply_flip(self, frame):
        """Apply flip to frame based on current flip_mode"""
        if self.flip_mode == 0:  # No flip
            return frame
        elif self.flip_mode == 1:  # Horizontal flip
            return cv2.flip(frame, 1)
        elif self.flip_mode == 2:  # Vertical flip
            return cv2.flip(frame, 0)
    
    def draw_overlay(self, frame):
        """Draw information overlays on the frame"""
        # Add recording indicator (red circle)
        if self.recording:
            cv2.circle(frame, (40, 35), 10, (0, 0, 255), -1)
            
            # Add recording time
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            timer_text = f"{mins:02d}:{secs:02d}"
            cv2.putText(frame, timer_text, (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Add current mode text
        mode_text = "Recording" if self.recording else "Preview"
        cv2.putText(frame, mode_text, (self.frame_width - 90, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add instructions
        cv2.putText(frame, "= Simple Video Recorder =", 
                   (10, self.frame_height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Space: Toggle Recording | F: Filter | R: Flip | ESC: Exit", 
                   (10, self.frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        try:
            while True:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Apply flip
                frame = self.apply_flip(frame)
                
                # Apply filter
                frame = self.apply_filter(frame)
                
                # Add overlays
                display_frame = self.draw_overlay(frame.copy())
                
                # Display frame
                cv2.imshow('Video Recorder', display_frame)
                
                # Write frame to output file if recording
                if self.recording and self.output is not None:
                    self.output.write(frame)
                
                # Process keyboard inputs
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC key
                    break
                elif key == 32:  # Space key
                    if self.recording:
                        self.stop_recording()
                        print("Recording stopped")
                    else:
                        self.start_recording()
                        print("Recording started")
                elif key == ord('f'):  # F key - change filter
                    self.filter_mode = (self.filter_mode + 1) % 4
                    print(f"Filter mode changed to {self.filter_mode}")
                elif key == ord('r'):  # R key - change flip
                    self.flip_mode = (self.flip_mode + 1) % 3
                    print(f"Flip mode changed to {self.flip_mode}")
                
        finally:
            # Clean up
            if self.recording:
                self.stop_recording()
            self.cap.release()
            cv2.destroyAllWindows()
            print("Application closed")


if __name__ == "__main__":
    try:
        recorder = VideoRecorder()
        recorder.run()
    except Exception as e:
        print(f"Error: {e}")