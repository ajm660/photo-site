document.addEventListener("alpine:init", () => {
  Alpine.data("lightboxGallery", (photos) => ({
    photos,
    active: null,
    touchX: null,

    open(index) {
      this.active = index;
    },

    close() {
      this.active = null;
    },

    current() {
      return this.active === null ? {} : this.photos[this.active];
    },

    prev() {
      if (this.active === null) return;
      this.active = (this.active - 1 + this.photos.length) % this.photos.length;
    },

    next() {
      if (this.active === null) return;
      this.active = (this.active + 1) % this.photos.length;
    },

    touchStart(event) {
      this.touchX = event.changedTouches[0].clientX;
    },

    touchEnd(event) {
      if (this.touchX === null) return;
      const delta = event.changedTouches[0].clientX - this.touchX;
      const SWIPE_THRESHOLD = 40;
      if (delta > SWIPE_THRESHOLD) {
        this.prev();
      } else if (delta < -SWIPE_THRESHOLD) {
        this.next();
      }
      this.touchX = null;
    },
  }));
});
