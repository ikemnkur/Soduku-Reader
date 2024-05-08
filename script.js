let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let image = null;
let isDragging = false;
let startX, startY;
let offsetX = 0;
let offsetY = 0;
let scale = 1;

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

document.getElementById('rotateSlider').addEventListener('input', function () {
  drawImage();
});

canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('mousemove', drag);
canvas.addEventListener('mouseup', stopDragging);
canvas.addEventListener('mouseout', stopDragging);

canvas.addEventListener('wheel', function (e) {
  e.preventDefault();
  let delta = e.deltaY > 0 ? 0.9 : 1.1;
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
  ctx.drawImage(image, -image.width / 2, -image.height / 2);
  ctx.restore();
}

document.getElementById('solveBtn').addEventListener('click', function () {
  let dataURL = canvas.toDataURL();
  // $.ajax({
  //   type: 'POST',
  //   // url: '/solve',
  //   url: 'http://127.0.0.1:5000/solve',
  //   data: { image: dataURL },
  //   success: function (response) {
  //     document.getElementById('result').innerHTML = response;
  //   }
  // });
  $.ajax({
    type: 'POST',
    url: 'http://localhost:5000/solve', 
    // url: 'http://127.0.0.1:5000/solve',
    data: { image: dataURL },
    success: function (response) {
      document.getElementById('result').innerHTML = response;
    }
  });
});