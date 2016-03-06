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
// need for plotting it up. The success handler for these AJAX requests then 
// calls the functions for displaying it.
for(var i=0; i < wallIds.length; i++){
    getWall(wallIds[i]);
}


// In the case that this is the arrangment page, set up other functionanality
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// If this is an arrangement page this variable will exist
var divArrange = $('.arrange-display');
var canvasArrange = $('.canvas-arrange');

var galleryId = $('.arrange-display').data('galleryid');

// save state of which walls have been generated most recently for each method
var recentCall = null;
var recentSaves = [];
var algorithmTypes = $('.arrange-select').map( function(){
    return $(this).data('algorithmtype');
}
);
var recentWalls = {};
for (i=0; i < algorithmTypes.length; i++){
    recentWalls[algorithmTypes[i]] = null;
}

// Listen for click on one of the arrangment icons
$('.arrange-select').click( function(){
    handleArrangeAlgorithmSelect($(this).data('algorithmtype')); }
);

// listen for click on refresh buttons which will prompt a new arrangment 
$('.rearrange-select').click( function(){
    requestArrange($(this).data('algorithmtype')); }
);

// listen for click on wall save button 
$('#save-button').click( function(){
    saveWall($(this).data('wallid')); }
);


function handleArrangeAlgorithmSelect(arrangeAlgorithm){
    // Given any algorithm selected, check if an arrangment exists as recently 
    // generated.  If not then request a new arrangement.  If it exists call wall handling.

    // Check this state holding variable from global scope
    var wallId = recentWalls[arrangeAlgorithm];

    if (wallId === null){
        // No wall associated yet with this algorithm type, request one.

        requestArrange(arrangeAlgorithm);

    } else {
        // There is one, just re-display it.
        handleArrangeWall(wallId);
    }
}

function requestArrange(arrangeAlgorithm){

    var postData = {'gallery_id': galleryId,
                    'algorithm_type': arrangeAlgorithm};

    recentCall = arrangeAlgorithm;

    // Make AJAX request for the wallId given
    $.post('arrange.json', postData, handleArrangeNewWall);
}

function handleArrangeNewWall(results){
    // Success handler for a brand new wall in the arrangment page.
    // JSON containing wallId was returned from AJAX request, so pass that along
    // to the function that handles plotting of new or recent walls in the 
    // arrangment page.

    var arrangeResults = results;

    var newWallId = arrangeResults.id;

    handleArrangeWall(newWallId);
}

function handleArrangeWall(wallId){

    // Set buttons and such for the the recent call that generated this wall
    // Get the wall plotting area ready for a new wall
    setArrangeWallDisplayed(wallId);
    clearCanvas();

    // Get and hang the new wall, this function is the same used for all wall
    // and gallery displays.
    getWall(wallId);
}

function setArrangeWallDisplayed(wallId){
    // function doing all the steps to reset the arrangment area and other data and 
    // buttons to reflect the current state

    // Set the display area to recieve the new wall via wall hanging functions
    divArrange.data('wallid', wallId);
    canvasArrange.attr('id', 'canvas' + wallId);

    // Set the trigger for type of arrangment to remember this most recent wall
    recentWalls[recentCall] = wallId;

    //Set save button to know which wall is displayed
    $('#save-div').show();
    $('#save-button').data('wallid', wallId);
    setSaveButtonState(wallId);

}

function saveWall(wallId){
    
    var postData = {'wall_id': wallId};

    // Make AJAX request for the wallId given
    $.post('save-wall.json', postData, handleSavedWall);
}

function handleSavedWall(results){

    wallId = results['wall_id'];

    recentSaves.push(wallId);
    setSaveButtonState(wallId);
}

function setSaveButtonState(wallId){

    if (recentSaves.indexOf(wallId) > -1){
        $('#save-button').hide();
        $('#save-confirm').show();
    } else {
        $('#save-button').show();
        $('#save-confirm').hide();
    }
}

function clearCanvas(){
    // Function to clear canvas so that a new wall may be displayed.

    context = canvasArrange[0].getContext('2d');
    context.clearRect(0, 0, canvasArrange[0].width, canvasArrange[0].height);
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

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

    // TODO: Use jquery here
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