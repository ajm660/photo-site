// Cloudinary Configuration
const CLOUDINARY_CLOUD_NAME = 'dkclin8yc';

// Function to create and add an image to the grid
const createImageElement = (src) => {
  const imgDiv = document.createElement('div');
  imgDiv.className = 'overflow-hidden rounded-md';

  const img = document.createElement('img');
  img.src = src;
  img.alt = 'Uploaded Image';
  img.className = 'w-full h-auto object-cover cursor-pointer rounded-md shadow-xl';

  // Add click event listener to toggle fullscreen
  img.addEventListener('click', () => toggleFullScreenImage(img));

  imgDiv.appendChild(img);
  return imgDiv;
};

// Function to reinitialize masonry for a section
const reinitializeMasonry = (section) => {
  const imageGrid = section.querySelector('.image-grid');
  imagesLoaded(imageGrid, function() {
    const width = window.innerWidth;
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

// Function to add uploaded image to section
const addUploadedImage = (imageUrl, sectionName) => {
  const sectionMap = { 'things': 'section1', 'places': 'section2', 'people': 'section3' };
  const sectionId = sectionMap[sectionName];
  const section = document.getElementById(sectionId);
  const imageGrid = section.querySelector('.image-grid');
  
  // Add new image at the beginning
  const imgElement = createImageElement(imageUrl);
  imageGrid.insertBefore(imgElement, imageGrid.firstChild);
  
  // Reinitialize masonry
  reinitializeMasonry(section);
};

// Function to load images dynamically for a section
const loadImages = (section) => {
    const folderPath = section.dataset.folder;
    const numberOfImages = section.dataset.count;
    const imageGrid = section.querySelector('.image-grid');
  
    for (let i = 1; i <= numberOfImages; i++) {
      const img = createImageElement(`${folderPath}/image-${i}.jpg`);
      imageGrid.appendChild(img);
    }

    // Initialize CSS Grid Masonry after images are loaded
    reinitializeMasonry(section);
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

// Upload Modal and Cloudinary Integration
const uploadModal = document.getElementById('uploadModal');
const uploadBtn = document.getElementById('uploadBtn');
const closeModal = document.getElementById('closeModal');
const openCloudinary = document.getElementById('openCloudinary');
const sectionSelect = document.getElementById('sectionSelect');

uploadBtn.addEventListener('click', () => {
  uploadModal.classList.remove('hidden');
});

closeModal.addEventListener('click', () => {
  uploadModal.classList.add('hidden');
});

uploadModal.addEventListener('click', (e) => {
  if (e.target === uploadModal) {
    uploadModal.classList.add('hidden');
  }
});

openCloudinary.addEventListener('click', () => {
  const selectedSection = sectionSelect.value;
  
  const cw = window.cloudinary.createUploadWidget(
    {
      cloudName: CLOUDINARY_CLOUD_NAME,
      uploadPreset: 'photo_site_unsigned', // Make sure to create this unsigned preset in Cloudinary
      folder: `photo-site/${selectedSection}`,
      tags: [selectedSection],
      resourceType: 'image',
      multiple: false,
      maxFileSize: 10000000 // 10MB
    },
    (error, result) => {
      if (!error && result && result.event === 'success') {
        const imageUrl = result.info.secure_url;
        addUploadedImage(imageUrl, selectedSection);
        uploadModal.classList.add('hidden');
      }
    }
  );
  
  cw.open();
});
  