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
// Alternately get the gallery ids to display
var galleryIds = $('.gallery-display').map( function(){
    return $(this).data('galleryid');
}
);

// For each wall_id that we found, make an ajax request to get the information 
// need for plotting it up.
for(var i=0; i < wallIds.length; i++){
    getWall(wallIds[i]);
}
for(var i=0; i < galleryIds.length; i++){
    getGallery(galleryIds[i]);
}

// Functions to handle getting wall info from server, then plotting it in canvas

function getWall(wallId){
    // Make AJAX request for the wallId given
    $.get('getwall.json', {'wallid':wallId}, handleWall);
}
function getGallery(galleryId){
    // Make AJAX request for the galleryId given
    $.get('getgallery.json', {'galleryid':galleryId}, handleWall);
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

    for (var picture in wallToHang.pictures_to_hang){
        // console.log("---"+picture);
        hangPicture(canvas, context, wallToHang.pictures_to_hang[picture], wallToCanvas);
    }
}


function hangPicture(canvas, context, picture, wallToCanvas){
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
        imageObj.onload = function() {context.drawImage(this,
                                                        xForCanvas,
                                                        yForCanvas,
                                                        wForCanvas,
                                                        hForCanvas
                                                        );
        };
    } else {
        // Draw a rectangle in case there is no image
        context.strokeRect(xForCanvas, yForCanvas, wForCanvas, hForCanvas);
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

