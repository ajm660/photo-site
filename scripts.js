// Function to load images dynamically for a section
const loadImages = (section) => {
    const folderPath = section.dataset.folder;
    const numberOfImages = section.dataset.count;
    const imageGrid = section.querySelector('.image-grid');
  
    for (let i = 1; i <= numberOfImages; i++) {
      const imgDiv = document.createElement('div');
      imgDiv.className = 'overflow-hidden rounded-lg shadow-lg p-1';
  
      const img = document.createElement('img');
      img.src = `${folderPath}/image-${i}.jpg`;
      img.alt = `Image ${i}`;
      img.className = 'w-full h-auto object-cover cursor-pointer';
  
      // Add click event listener to toggle fullscreen
      img.addEventListener('click', () => toggleFullScreenImage(img));
  
      imgDiv.appendChild(img);
      imageGrid.appendChild(imgDiv);
    }

    // Initialize CSS Grid Masonry after images are loaded
    imagesLoaded(imageGrid, function() {
      const width = window.innerWidth; // Use window width for breakpoints
      let numColumns;
      if (section.id === 'section1') {
        if (width < 768) numColumns = 2;
        else if (width < 1024) numColumns = 3;
        else if (width < 1280) numColumns = 4;
        else numColumns = 6;
      } else {
        if (width < 640) numColumns = 1;
        else if (width < 768) numColumns = 2;
        else if (width < 1024) numColumns = 3;
        else if (width < 1280) numColumns = 4;
        else numColumns = 6;
      }
      imageGrid.style.display = 'grid';
      imageGrid.style.gridTemplateRows = 'masonry';
      imageGrid.style.gridTemplateColumns = `repeat(${numColumns}, 1fr)`;
      imageGrid.style.gap = '10px';
    });
  };
  
  // Function to toggle fullscreen mode for an image
  const toggleFullScreenImage = (image) => {
    const existingOverlay = document.querySelector('#image-overlay');
    if (existingOverlay) {
      // If overlay exists, remove it to close the fullscreen image
      existingOverlay.remove();
      document.body.classList.remove('overflow-hidden');
    } else {
      // Create overlay to display fullscreen image
      const overlay = document.createElement('div');
      overlay.id = 'image-overlay';
      overlay.className = 'fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50';
      overlay.addEventListener('click', () => toggleFullScreenImage(image));
  
      // Clone the image for fullscreen view
      const fullImage = image.cloneNode(true);
      fullImage.className = 'max-w-full max-h-full';
  
      overlay.appendChild(fullImage);
      document.body.appendChild(overlay);
      document.body.classList.add('overflow-hidden');
    }
  };
  
  // Intersection Observer to detect when sections are in view
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const section = entry.target;
        loadImages(section); // Load images for the section
        observer.unobserve(section); // Stop observing after loading
      }
    });
  });
  
  // Observe all sections with the class "lazy-section"
  document.querySelectorAll('.lazy-section').forEach((section) => {
    observer.observe(section);
  });
  