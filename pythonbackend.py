from flask import Flask, request, jsonify
import cv2
import numpy as np
import matplotlib as plt

# Import your Sudoku solver here
def solve(image):
    plt.figure(figsize=(4, 4))
    plt.imshow(image, cmap='gray')
    plt.title('Uploaded Sudoku Image')
    plt.axis('off')
    plt.show()

app = Flask(__name__)

@app.route('/solve', methods=['POST'])
def solve_sudoku():
    image_data = request.form['image']
    # Process the image data (remove the data URL prefix)
    image_data = image_data.split(',')[1]
    # Decode the base64 image data
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    # Read the image using OpenCV
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Perform necessary image processing and solve the Sudoku puzzle
    # using your Sudoku solver
    solution = solve(image)
    
    return jsonify(solution)

if __name__ == '__main__':
    app.run()