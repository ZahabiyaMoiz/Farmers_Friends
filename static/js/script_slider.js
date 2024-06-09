// // Wrap the logic in a function to execute it after the DOM is loaded
// document.addEventListener("DOMContentLoaded", function() {
//     const items = document.querySelectorAll('.single-item');
//     let currentPosition = 0;
//     const itemWidth = items[0].offsetWidth; // Assuming all items have the same width

//     function slide(direction) {
//         if (direction === 'next' && currentPosition > -(items.length - 1) * itemWidth) {
//             currentPosition -= itemWidth;
//         } else if (direction === 'prev' && currentPosition < 0) {
//             currentPosition += itemWidth;
//         }
//         for (let i = 0; i < items.length; i++) {
//             items[i].style.transform = `translateX(${currentPosition}px)`;
//         }
//     }

//     // Optional: Add event listeners for buttons to slide items
//     document.getElementsByClassName('prevBtn').addEventListener('click', function() {
//         slide('prev');
//     });

//     document.getElementsByClassName('nextBtn').addEventListener('click', function() {
//         slide('next');
//     });
// });
