## ♻️ Ecoforest
Real-time waste detection and classification using YOLO, OpenCLIP, Next.js, and FastAPI.

WasteVision is a computer-vision web application that uses a live webcam feed to identify objects and suggest waste-disposal categories. The browser displays the camera feed while a Python backend processes sampled frames using YOLO object detection and OpenCLIP classification.

Project status: Local development prototype. The live-classification frontend is designed to send frames automatically; end-to-end model performance and deployment have not been independently verified.


### Features
Live webcam preview in a dashboard
Automatic frame classifications 
YOLO-based object detection and OpenCLIP-based classification
Predicted item names, disposal routes, and confidence scores (when returned by the backend)
Optional bounding-box overlays for detections with pixel-coordinate bounding boxes
Request sequencing to avoid overlapping inference calls
