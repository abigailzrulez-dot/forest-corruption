<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoForest - Waste Scanner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .camera-container {
            position: relative;
            width: 100%;
            aspect-ratio: 4/3;
            background: #000;
            border-radius: 10px;
            overflow: hidden;
        }
        
        #camera {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .scan-button {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s, background 0.2s;
        }
        
        .scan-button:hover {
            transform: translateY(-2px);
            background: #45a049;
        }
        
        .scan-button:active {
            transform: translateY(0);
        }
        
        .scan-button.scanning {
            background: #f44336;
        }
        
        .results-container {
            margin-top: 20px;
        }
        
        .result-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #4CAF50;
        }
        
        .result-item.recycling {
            border-left-color: #2196F3;
        }
        
        .result-item.composting {
            border-left-color: #8BC34A;
        }
        
        .result-item.trash {
            border-left-color: #9E9E9E;
        }
        
        .result-item.eco-brick {
            border-left-color: #FF9800;
        }
        
        .result-item h3 {
            color: #333;
            margin-bottom: 5px;
        }
        
        .result-item p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .close-button {
            position: absolute;
            top: 20px;
            right: 20px;
            background: #f44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .status-dot.inactive {
            background: #f44336;
        }
        
        .status-text {
            font-size: 0.9rem;
            color: #666;
        }
        
        .confidence-bar {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: #4CAF50;
            border-radius: 4px;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌳 EcoForest Waste Scanner</h1>
            <p>Point your camera at items to identify where they belong</p>
        </div>
        
        <div class="main-content">
            <div class="card">
                <h2>📷 Live Scanner</h2>
                
                <div class="status-indicator">
                    <div class="status-dot inactive" id="statusDot"></div>
                    <span class="status-text" id="statusText">Camera inactive</span>
                </div>
                
                <div class="camera-container">
                    <video id="camera" autoplay playsinline muted></video>
                    <button class="scan-button" id="scanButton">Start Scan</button>
                    <button class="close-button" id="closeButton">Close</button>
                </div>
                
                <div class="results-container" id="resultsContainer">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Results will appear here...</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Scanner Status</h2>
                <div class="status-indicator">
                    <div class="status-dot" id="serverDot"></div>
                    <span class="status-text" id="serverText">Checking connection...</span>
                </div>
                
                <div class="status-indicator">
                    <div class="status-dot" id="modelDot"></div>
                    <span class="status-text" id="modelText">Loading models...</span>
                </div>
                
                <div class="status-indicator">
                    <div class="status-dot" id="detectionDot"></div>
                    <span class="status-text" id="detectionText">No detections</span>
                </div>
                
                <h3>Recent Detections</h3>
                <div id="recentDetections">
                    <p class="status-text">No detections yet</p>
                </div>
                
                <h3>Category Distribution</h3>
                <div id="categoryDistribution">
                    <p class="status-text">No data yet</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Scanner application
        const camera = document.getElementById('camera');
        const scanButton = document.getElementById('scanButton');
        const closeButton = document.getElementById('closeButton');
        const resultsContainer = document.getElementById('resultsContainer');
        const recentDetections = document.getElementById('recentDetections');
        const categoryDistribution = document.getElementById('categoryDistribution');
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const serverDot = document.getElementById('serverDot');
        const serverText = document.getElementById('serverText');
        const modelDot = document.getElementById('modelDot');
        const modelText = document.getElementById('modelText');
        const detection