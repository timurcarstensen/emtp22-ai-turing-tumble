enum Part {
  NotValid = -100,
  Valid = 0,
  GreenLeft = 1,
  GreenRight = 2,
  Orange = 3,
  Red = 4,
  BlueLeft = 5,
  BlueWheelLeft = 7,
  Black = 6,
  BlueWheelRight = 8,
  BlueRight = 9,
  LightGrey = -100,
  DarkGrey = -100,
}
const colors = {
  notValid: [32, 32, 32, 254],
  red: [189, 0, 0, 255],
  red2: [255,0,0,255],
  greenRight: [0, 255, 0, 255],
  greenLeft: [0, 189, 0, 255],
  orange: [255, 128, 0, 255],
  blueLeft: [0, 255, 255, 255],
  blueWheelLeft: [128, 0, 255, 255],
  black: [0, 0, 0, 255],
  white: [255, 255, 255, 255],
  blueWheelRight: [96, 0, 189, 255],
  blueRight: [0, 189, 189, 255],
  lightGrey: [128, 128, 128, 254],
  darkGrey: [96, 96, 96, 254],
};

const loadImage = (path: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "Anonymous"; // to avoid CORS if used with Canvas
    img.src = path;
    img.onload = () => {
      resolve(img);
    };
    img.onerror = (e) => {
      reject(e);
    };
  });
};

//Function that transforms the image to matrix (Board -> Matrix Converter)
export const transformToMatrix = async (url: string) => {
  // url is a base64 encoded image
  let img = await loadImage(url);
  let cvs = document.createElement("canvas");
  cvs.width = 13;
  cvs.height = 18;
  const matrix: number[][] = [];
  let ctx = cvs.getContext("2d");
  ctx.drawImage(img, 0, 0);
  const imageData = ctx.getImageData(0, 0, cvs.width, cvs.height);
  const pixels = imageData.data;
  /* pixels is an array containing imgWidth * imgHeight * 4 elemets
      "* 4" because every pixel has 4 numbers coresponding for its rgba value
  */
  const pixelArr = []; // group every 4 pixels (for simplicity)
  for (let i = 0; i < pixels.length; i += 4) {
    const pixelGroup = [pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3]];
    pixelArr.push(pixelGroup);
  }
  let pixelMatrix = transformArrToMatrix(pixelArr); // transform the array in a matrix
  // translate the colors into parts
  for (let i = 2; i < 13; i++) {
    const row = [];
    for (let j = 1; j < 12; j++) {
      row.push(translateColor(pixelMatrix[i][j]));
    }
    matrix.push(row);
  }
  return matrix;
};

function arrayEquals(a: number[], b: number[]) {
  return a.every((val, index) => val === b[index]);
}

const translateColor = (color: number[]) => {
  console.log("Ich bin am Anfang.")
  console.log("Hier ein Pixel");
  console.log(color);
  if (arrayEquals(color, colors.notValid)) {
    return Part.NotValid;
  }
  if (arrayEquals(color, colors.red)) {
    return Part.Red;
  }
  if (arrayEquals(color, colors.red2)) {
    return Part.Red;
  }
  if (arrayEquals(color, colors.greenRight)) {
    return Part.GreenRight;
  }
  if (arrayEquals(color, colors.greenLeft)) {
    return Part.GreenLeft;
  }
  if (arrayEquals(color, colors.orange)) {
    return Part.Orange;
  }
  if (arrayEquals(color, colors.blueLeft)) {
    return Part.BlueLeft;
  }
  if (arrayEquals(color, colors.blueWheelLeft)) {
    return Part.BlueWheelLeft;
  }
  if (arrayEquals(color, colors.black)) {
    return Part.Black;
  }
  if (arrayEquals(color, colors.white)) {
    return Part.Valid;
  }
  if (arrayEquals(color, colors.blueWheelRight)) {
    return Part.BlueWheelRight;
  }
  if (arrayEquals(color, colors.blueRight)) {
    return Part.BlueRight;
  }
  if (arrayEquals(color, colors.darkGrey)) {
    return Part.DarkGrey;
  }
  if (arrayEquals(color, colors.lightGrey)) {
    return Part.LightGrey;
  }
  console.log(color);
  console.log("Ich bin am Ende.")
  return -100;
};

const transformArrToMatrix = (arr: number[][]) => {
  let matrix = [];
  for (let i = 0; i < 18; i++) {
    let row = [];
    for (let j = 0; j < 13; j++) {
      row.push(arr[i * 13 + j]);
    }
    matrix.push(row);
  }
  return matrix;
};
