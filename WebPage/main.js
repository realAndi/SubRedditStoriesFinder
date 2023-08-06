document.getElementById('screenshot-button').addEventListener('click', function() {
    html2canvas(document.querySelector(".post-container"), { scale: 2 }).then(canvas => {
        // Create a new Image object
        var img = new Image();

        // Set the img src to the canvas data url
        img.src = canvas.toDataURL();

        // Set the width and height of the image to the width and height of the container
        img.style.width = document.querySelector(".post-container").offsetWidth + 'px';
        img.style.height = document.querySelector(".post-container").offsetHeight + 'px';

        // Append the image to the body
        document.body.appendChild(img);
    });
});
