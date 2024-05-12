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
  ctx2.translate(transformedImgCanvas.width / 2, transformedImgCanvas.height / 2);
  flipX *= -1;
  ctx2.scale(flipX, 1);
  ctx2.drawImage(originalImage, -transformedImgCanvas.width / 2, -transformedImgCanvas.height / 2, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.restore();
  img.src = transformedImgCanvas.toDataURL();
  originalImage = img
});

flipY = 1;  // 1 for normal, -1 for flipped

// Event listener for the Flip Y button
document.getElementById('flipYBtn').addEventListener('click', function () {
  ctx2.clearRect(0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.save();
  ctx2.translate(transformedImgCanvas.width / 2, transformedImgCanvas.height / 2);
  flipY *= -1;
  ctx2.scale(1, flipY);
  ctx2.drawImage(originalImage, 0, 0, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.drawImage(originalImage, -transformedImgCanvas.width / 2, -transformedImgCanvas.height / 2, transformedImgCanvas.width, transformedImgCanvas.height);
  ctx2.restore();
  img.src = transformedImgCanvas.toDataURL();
  originalImage = img;
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
  originalImage = img;
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
    }
  });
});

let sudokuMatrix = null;
let solvedMatrix = null;

// Event listener for the Solve button
document.getElementById('solveBtn').addEventListener('click', function () {
  let dataURL = img.src;
  $.ajax({
    type: 'POST',
    url: 'http://localhost:5000/solve',
    data: { image: dataURL },
    success: function (response) {
      console.log(response);
      document.getElementById('result').innerHTML = 'Input to Text:<br>' + response;
      // loadTransformedImage(response);
      sudokuMatrix = stringToMatrix(response);
      console.log("SG: ", sudokuMatrix);
      solvedMatrix = solveSudoku(response);
      displaySolvedSudoku(solvedMatrix)
    },
    error: function (xhr, status, error) {
      console.error('Error:', error);
    }
  });
});

function stringToMatrix(str) {
  // Remove the outer square brackets
  str = str.slice(1, -1);

  // Split the string into rows
  const rows = str.split('] [');

  // Map each row to an array of numbers
  const matrix = rows.map(row => {
    return row.split(' ').map(Number);
  });

  return matrix;
}

function solveSudoku(str) {
  // Remove non-numeric characters from the string
  const digits = str.replace(/\D/g, '');

  // Create a 9x9 matrix from the digits
  const grid = [];
  for (let i = 0; i < 9; i++) {
    grid.push(digits.slice(i * 9, (i + 1) * 9).split('').map(Number));
  }

  function isValid(row, col, num) {
    // Check row
    for (let i = 0; i < 9; i++) {
      if (grid[row][i] === num) {
        return false;
      }
    }

    // Check column
    for (let i = 0; i < 9; i++) {
      if (grid[i][col] === num) {
        return false;
      }
    }

    // Check 3x3 box
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    for (let i = boxRow; i < boxRow + 3; i++) {
      for (let j = boxCol; j < boxCol + 3; j++) {
        if (grid[i][j] === num) {
          return false;
        }
      }
    }

    return true;
  }

  function findEmptyCell() {
    for (let row = 0; row < 9; row++) {
      for (let col = 0; col < 9; col++) {
        if (grid[row][col] === 0) {
          return [row, col];
        }
      }
    }
    return null;
  }

  function solve() {
    const emptyCell = findEmptyCell();
    if (emptyCell === null) {
      return true; // Sudoku is solved
    }

    const [row, col] = emptyCell;
    for (let num = 1; num <= 9; num++) {
      if (isValid(row, col, num)) {
        grid[row][col] = num;
        if (solve()) {
          return true;
        }
        grid[row][col] = 0; // Backtrack
      }
    }

    return false; // No valid solution found
  }

  solve();
  return grid;
}

function displaySolvedSudoku(solvedGrid) {
  // Create a table element
  const table = document.getElementById('grid');
  // reset the table
  table.innerHTML = "";
  // Iterate over each row of the solved grid
  for (let row = 0; row < 9; row++) {
    const tr = document.createElement('tr');

    // Iterate over each column of the solved grid
    for (let col = 0; col < 9; col++) {
      const td = document.createElement('td');
      td.textContent = solvedGrid[row][col];
      
      td.style.border = '2px solid black';
      // Add borders to create the Sudoku grid layout
      if (col === 2 || col === 5) {
        td.style.borderRight = '3px solid black';
      } 
      if (row === 2 || row === 5) {
        td.style.borderBottom = '3px solid black';
      } 
      
     

      tr.appendChild(td);
    }

    table.appendChild(tr);
  }

  // Add the table to the page
  document.body.appendChild(table);
}
