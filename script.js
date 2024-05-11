let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let image = null;
let isDragging = false;
let startX, startY;
let offsetX = 0;
let offsetY = 0;
let scale = 1;

let scanResult = null;
let solveResult = null;

document.getElementById('fileInput').addEventListener('change', function (e) {
  let file = e.target.files[0];
  let reader = new FileReader();
  reader.onload = function (event) {
    image = new Image();
    image.onload = function () {
      drawImage();
    };
    image.src = event.target.result;
  };
  reader.readAsDataURL(file);
});

document.getElementById('rotateValue').addEventListener('input', function () {
  document.getElementById('rotateSlider').value = this.value;
  drawImage();
});

document.getElementById('rotateSlider').addEventListener('input', function () {
  document.getElementById('rotateValue').value = this.value;  
  drawImage();
});

canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('mousemove', drag);
canvas.addEventListener('mouseup', stopDragging);
canvas.addEventListener('mouseout', stopDragging);

canvas.addEventListener('wheel', function (e) {
  e.preventDefault();
  let delta = e.deltaY > 0 ? 0.95 : 1.05;
  scale *= delta;
  drawImage();
});

function startDragging(e) {
  if (image) {
    isDragging = true;
    startX = e.clientX - offsetX;
    startY = e.clientY - offsetY;
  }
}

function drag(e) {
  if (isDragging) {
    offsetX = e.clientX - startX;
    offsetY = e.clientY - startY;
    drawImage();
  }
}

function stopDragging() {
  isDragging = false;
}

function drawImage() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(canvas.width / 2 + offsetX, canvas.height / 2 + offsetY);
  ctx.rotate(document.getElementById('rotateSlider').value * Math.PI / 180);
  ctx.scale(scale, scale);
  ctx.rect(-canvas.width, -canvas.height, 2*canvas.width, 2*canvas.height);
  ctx.fillStyle = "white";
  ctx.fill();
  ctx.drawImage(image, -image.width / 2, -image.height / 2);
  ctx.restore();
}

const transformedImgCanvas = document.getElementById('transformedImgCanvas');
const ctx2 = transformedImgCanvas.getContext('2d');
const img = document.getElementById('img');

let originalImage = null;

// Function to load the transformed image onto the canvas
function loadTransformedImage(response) {
  const transformedImage = new Image();
  transformedImage.onload = function () {
    ctx2.drawImage(transformedImage, 0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
    originalImage = transformedImage;
  };
  transformedImage.src = 'data:image/png;base64,' + response.image;
}

flipX = 1;  // 1 for normal, -1 for flipped

// Event listener for the Flip X button
document.getElementById('flipXBtn').addEventListener('click', function () {
  ctx2.clearRect(0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.save();
  flipX *= -1;
  ctx2.scale(flipX, 1);
  ctx2.drawImage(originalImage, -transformedImgCanvas.width, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.restore();
  img.src = transformedImgCanvas.toDataURL();
});

flipY = 1;  // 1 for normal, -1 for flipped

// Event listener for the Flip Y button
document.getElementById('flipYBtn').addEventListener('click', function () {
  ctx2.clearRect(0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.save();
  flipY *= -1;
  ctx2.scale(1, flipY);
  ctx2.drawImage(originalImage, 0, -transformedImgCanvas.height, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.restore();
  img.src = transformedImgCanvas.toDataURL();
});

rotatation = 0; // 0 for normal, Math.PI/2 for 90 degrees, Math.PI for 180 degrees, 3*Math.PI/2 for 270 degrees

// Event listener for the Rotate button
document.getElementById('rotateBtn').addEventListener('click', function () {
  ctx2.clearRect(0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.save();
  ctx2.translate(transformedImgCanvas.width / 2, transformedImgCanvas.height / 2);
  rotatation += (Math.PI / 2) % (2 * Math.PI);
  ctx2.rotate(rotatation);
  ctx2.drawImage(originalImage, -transformedImgCanvas.width / 2, -transformedImgCanvas.height / 2, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.restore();
  img.src = transformedImgCanvas.toDataURL();
});


document.getElementById('scanBtn').addEventListener('click', function () {
  let dataURL = canvas.toDataURL();
  $.ajax({
    type: 'POST',
    url: 'http://localhost:5000/scan', 
    // url: 'http://127.0.0.1:5000/solve',
    data: { image: dataURL },
    success: function (response) {
      scanResult = response;
      console.log(response);
      document.getElementById('result').innerHTML = response;

      // Create a new canvas for the transformed image
      let transformedCanvas = document.getElementById("transformedImgCanvas"); //document.createElement('canvas');
      // transformedCanvas.width = 500;
      // transformedCanvas.height = 500;
      let transformedCtx = transformedCanvas.getContext('2d');
      
      // Create an image object from the received base64 image data
      let transformedImage = new Image();
      transformedImage.onload = function () {
        // Draw the transformed image on the new canvas
        transformedCtx.drawImage(transformedImage, 0, 0, transformedCanvas.width, transformedCanvas.height);
      };
      transformedImage.src = 'data:image/png;base64,' + response.image;
      let img = document.getElementById("img");
      img = transformedImage;
      loadTransformedImage(response);
      // Append the transformed canvas to the result div
      // document.getElementById('result').appendChild(transformedCanvas);
    }
  });
});

// Event listener for the Solve button
document.getElementById('solveBtn').addEventListener('click', function () {
  let dataURL = img.src;
  $.ajax({
    type: 'POST',
    url: 'http://localhost:5000/solve',
    data: { image: dataURL },
    success: function (response) {
      document.getElementById('result').innerHTML = 'Solution:<br>' + response.solution;
      loadTransformedImage(response);
    },
    error: function (xhr, status, error) {
      console.error('Error:', error);
    }
  });
});

// document.getElementById('solveBtn').addEventListener('click', function () {
//   let dataURL = canvas.toDataURL();
//   $.ajax({
//     type: 'POST',
//     url: 'http://localhost:5000/solve', 
//     // url: 'http://127.0.0.1:5000/solve',
//     data: { image: dataURL },
//     success: function (response) {
//       solveResult = response; 
//       document.getElementById('result').innerHTML = response;
//     }
//   });
// });