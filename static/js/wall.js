// Parameters to use in rescalling walls
// TODO: decide where to store these or get them from screen size infromation
maxCanvasHeight = 300;
maxCanvasWidth = 900;


// Get the wall_ids that I'm going to need to fill into canvases
// Note to self, this is some hard won synthax... each()
// did not allow me to return the information.
var wallIds = $('.wall-display').map( function(){
    return $(this).data('wallid');
}
);

// For each wall_id that we found, make an ajax request to get the information 
// need for plotting it up.
for(var i=0; i < wallIds.length; i++){
    getWall(wallIds[i]);
}


// In the case that this is the arrangment page, set up a bunch of other functionanality

// save state of which walls have been genrated in this visit to the page

// Listen for click on one of the arrangment icons
    // clear canvas and redraw if already generated
    // if not already there then request an arrangment and then plot

// listen for click on refresh buttons which would prompt a new arrangment and 
// reset of the state for each arrangemnet type


// - - - - - - - - - - - - - - - - - -

// Functions to handle getting wall info from server, then plotting it in canvas

function getWall(wallId){
    // Make AJAX request for the wallId given
    $.get('getwall.json', {'wallid':wallId}, handleWall);
}

function handleWall(results){
    // For wall returned from AJAX request, see if a wall was found.
    // If so plot it, otherwise give some information
    var wallToHang = results;

    if (wallToHang['id'] !== null) {
        // console.dir(wallToHang);
        hangWall(wallToHang);
    } else {
        console.log("This is not the wall you're looking for.");
    }
}


function hangWall(wallToHang){
    // Draw the pictures of a wall on a canvas.

    var canvas = document.getElementById('canvas'+wallToHang.id);
    var context = canvas.getContext('2d');

    var wallToCanvas = getWallDisplayScale(wallToHang);

    var picturesToHangOrdered = getHangOrder(wallToHang.pictures_to_hang);

    if (wallToHang.is_gallery){
        var firstPicture = wallToHang.pictures_to_hang[picturesToHangOrdered[0]];
        var nearBottomFirstPicture = (firstPicture.y * wallToCanvas.scale + wallToCanvas.y_offset +
                                  firstPicture.height * wallToCanvas.scale * 0.9);
        drawFloor(context, nearBottomFirstPicture);
    }

    for (var i=0; i < picturesToHangOrdered.length; i++){
        // console.log("---"+picture);
        var picture = picturesToHangOrdered[i];
        hangPicture(context, wallToHang.pictures_to_hang[picture], wallToCanvas);
    }
}

function hangPicture(context, picture, wallToCanvas){
    // Draw picture on a wall in placement.

    // Convert placement coordinates and size to canvas size
    var xForCanvas = picture.x * wallToCanvas.scale + wallToCanvas.x_offset;
    var yForCanvas = picture.y * wallToCanvas.scale + wallToCanvas.y_offset;
    var wForCanvas = picture.width * wallToCanvas.scale;
    var hForCanvas = picture.height * wallToCanvas.scale;

    // If availible draw in the image
    if(picture.image !== null){
        var imageObj = new Image();
        imageObj.src = picture.image;

        // Event listener for when the image has loaded, src may need to be 
        // placed after this acording to some advice?
        imageObj.onload = function() {
            context.drawImage(this, xForCanvas, yForCanvas, wForCanvas, hForCanvas);
        };
        imageObj.onerror = function() {
           // If image not loaded draw rectangle
            hangEmptyPicture(context, xForCanvas, yForCanvas, wForCanvas, hForCanvas);
        };
    } else {
        hangEmptyPicture(context, xForCanvas, yForCanvas, wForCanvas, hForCanvas);
    }
}


function getWallDisplayScale(wallToHang){
    // Get the scale so that the wall can be displayed as large as possible 
    // within limit parameters for maximum canvas width or height.

    var widthRatio = maxCanvasWidth / wallToHang.width;
    var heightRatio = maxCanvasHeight / wallToHang.height;
    var scale = Math.floor(Math.min( widthRatio, heightRatio ));

    var x_offset = (maxCanvasWidth - (wallToHang.width * scale)) / 2;
    var y_offset = (maxCanvasHeight - (wallToHang.height * scale)) / 2;

    wallToCanvas = {'scale': scale,
                    'x_offset': x_offset,
                    'y_offset': y_offset
                    };

    return wallToCanvas;
}

function getHangOrder(picturesToHang){
    var pictureKeys = Object.keys(picturesToHang);

    pictureKeys.sort(function(x,y){
        return Math.sign(picturesToHang[y].height - picturesToHang[x].height);
    }
    );

    return pictureKeys;
}

function hangEmptyPicture(context, xForCanvas, yForCanvas, wForCanvas, hForCanvas){
    
    context.fillStyle = '#A9A9A9';
    context.fillRect(xForCanvas, yForCanvas, wForCanvas, hForCanvas);
    // context.stroke();
    context.strokeStyle = '#000000';
    context.lineWidth = 2;
    context.strokeRect(xForCanvas, yForCanvas, wForCanvas, hForCanvas);
    // context.stroke();
}

function drawFloor(ctx, hFloor){
    var wFloor = 900;
    // var hFloor = 150;
    var dFloor = 60;

    var x = 0;
    var v = 0;
    while(x < (900 + dFloor)){
        x = x + 15;
        v = dFloor * 0.1 * Math.random();
        ctx.beginPath();
        ctx.moveTo(x,hFloor);
        ctx.lineTo(x-dFloor-v,hFloor+dFloor+v);
        ctx.strokeStyle="#999999";
        ctx.stroke();
        ctx.closePath();
    }

    x = 0;
    while(x < (900 + dFloor)){
        x = x + 15;
        v = dFloor * 0.1 * Math.random();
        ctx.beginPath();
        ctx.moveTo(x,hFloor);
        ctx.lineTo(x,(hFloor-dFloor*0.5+v));
        ctx.strokeStyle="#ECECEC";
        ctx.stroke();
        ctx.closePath();
    }

    ctx.beginPath();
    ctx.moveTo(0,hFloor);
    ctx.lineTo(wFloor,hFloor);
    ctx.strokeStyle="#4B4B4B";
    ctx.stroke();
    ctx.closePath();
}