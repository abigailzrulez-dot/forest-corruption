## ♻️ Ecoforest
Real-time waste detection and classification using YOLO, OpenCLIP, Next.js, and FastAPI.

WasteVision is a computer-vision web application that uses a live webcam feed to identify objects and suggest waste-disposal categories. The browser displays the camera feed while a Python backend processes sampled frames using YOLO object detection and OpenCLIP classification.

Project status: Local development prototype. The live-classification frontend is designed to send frames automatically; end-to-end model performance and deployment have not been independently verified.

## Inspiration
Ecoforest was inspired by our desire to make recycling more accessible, intuitive, and environmentally friendly. We recognized a common problem in everyday waste management: many people unknowingly place contaminated or non-recyclable items into recycling bins, potentially compromising the recycling process. We wanted to address this issue by creating an AI-powered web application that helps users identify waste and understand how to dispose of it properly. Our goal is to make sustainable habits easier to adopt and encourage environmentally conscious decisions.

## What it does
Ecoforest is an interactive web application that uses computer vision to identify everyday objects and provide guidance on how to dispose of them responsibly. Using a YOLOv8 object detection model, the application identifies items through a camera feed and classifies them into appropriate waste categories, helping users determine whether an item should be recycled or discarded.

Beyond waste classification, Ecoforest incorporates a gamified sustainability experience. Users can complete eco-friendly tasks and check them off on their dashboard, gradually transforming a virtual forest into a greener, healthier environment. This feature encourages users to build sustainable habits while visualizing the impact of their actions.

## How we built it
We developed Ecoforest using a combination of modern web development technologies and machine learning frameworks.

Frontend: React and Next.js for building an interactive, user-friendly interface.
Backend: FastAPI for handling communication between the frontend and the machine learning model.
Computer Vision: Ultralytics YOLOv8 for real-time object detection and waste classification.
Dashboard Design: We used Claude to assist with generating and refining the dashboard interface.

## Challenges we ran into
- Lack of knowledge about web development and the implementation of AI into software
- Issues with teammate availability throughout the hackathon
- Hardware availability
- Transferring HTML to React 

## Accomplishments that we're proud of
We are especially proud of developing a functional web application that combines computer vision with an interactive sustainability dashboard.

Our biggest accomplishment was successfully integrating a YOLOv8 object detection model with a FastAPI backend and React/Next.js frontend, allowing users to identify waste items through a live camera feed.

We are also proud of creating a visually engaging dashboard that makes sustainability more interactive through task completion and virtual forest growth. Bringing these components together during a time-constrained hackathon was a significant achievement for our team.

## What we learned
Building Ecoforest gave us valuable hands-on experience in both software engineering and applied artificial intelligence.
- Integrating a FastAPI backend with a computer vision model.
- Connecting a React/Next.js frontend to backend APIs.
- Working with HTML, React, and other web development technologies.
- Designing interactive and responsive user interfaces.
- Collaborating effectively under tight deadlines and adapting to unexpected technical challenges.

## What's next for Ecoforest
We envision Ecoforest evolving into a more comprehensive smart waste management platform.

One of our next goals is to support remote camera integration, allowing users to monitor and classify waste from different locations throughout their homes. We also want to expand our computer vision capabilities to detect and classify multiple waste items simultaneously, providing users with a complete breakdown of how to sort a larger collection of trash.

In the future, we hope to improve classification accuracy, expand the range of supported waste categories, and provide more detailed disposal recommendations based on local recycling guidelines.

Ultimately, our vision is to make Ecoforest an accessible, intelligent tool that helps people make more sustainable decisions in their everyday lives.
