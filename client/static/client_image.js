'use strict'

function dynamic_image() {
    let image_upload = document.getElementsByName('img').item(0)
    let image_preivew = document.getElementsByTagName('img').item(0)
    // make temp directory put the image in adn remove it when saves the client if it exists in the dir
    image_upload.addEventListener('change', function () {
        image_upload.value.split("\\").pop()
    })
}

// window.addEventListener('load', dynamic_image)