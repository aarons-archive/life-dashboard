import { Toast } from 'bootstrap';
import imagesLoaded from 'imagesloaded';

import Masonry from 'masonry-layout';
import '../css/app.scss';


// Masonry
const masonryGrids = document.querySelectorAll('.masonry');

masonryGrids.forEach(element => {

    const masonry = new Masonry(element, {
        percentPosition: true,
    });

    imagesLoaded(element, () => {
        masonry.layout();
    });

});


// Toasts
const toastNoPermissionElements = document.querySelectorAll('.no-permission-toast');

toastNoPermissionElements.forEach(element => {

    element.addEventListener('click', () => {
        const toast = new Toast(document.getElementById('noPermissionToast'));
        toast.show();
    });

});
