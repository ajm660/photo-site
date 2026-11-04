// Keep DOM and lightbox order intact while packing newest photos from the top.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".masonry-gallery").forEach((gallery) => {
    const items = Array.from(gallery.querySelectorAll(":scope > a"));
    if (!items.length) return;

    let frame;
    const layout = () => {
      const styles = getComputedStyle(gallery);
      const columns = Number(styles.getPropertyValue("--gallery-columns"));
      const gap = parseFloat(styles.columnGap) || 0;
      const width = (gallery.clientWidth - gap * (columns - 1)) / columns;
      if (width <= 0) return;
      const heights = Array(columns).fill(0);
      gallery.dataset.masonry = "";

      items.forEach((item) => {
        const column = heights.indexOf(Math.min(...heights));
        item.style.width = `${width}px`;
        item.style.left = `${column * (width + gap)}px`;
        item.style.top = `${heights[column]}px`;
        heights[column] += item.getBoundingClientRect().height + gap;
      });
      gallery.style.height = `${Math.max(...heights) - gap}px`;
    };
    const scheduleLayout = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(layout);
    };
    items.forEach((item) => {
      const image = item.querySelector("img");
      const reveal = () => {
        image.classList.add("is-loaded");
        scheduleLayout();
      };
      image.addEventListener("load", reveal);
      image.addEventListener("error", reveal);
      if (image.complete) image.classList.add("is-loaded");
    });
    let previousWidth;
    new ResizeObserver(([entry]) => {
      if (entry.contentRect.width !== previousWidth) {
        previousWidth = entry.contentRect.width;
        scheduleLayout();
      }
    }).observe(gallery);
    layout();
  });
});

document.addEventListener("alpine:init", () => {
  Alpine.data("contactForm", () => ({
    status: "idle",

    async submit(event) {
      const form = event.target;
      this.status = "sending";
      try {
        const response = await fetch(form.action, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.message);
        form.reset();
        this.status = "sent";
      } catch {
        this.status = "error";
      }
    },
  }));

  Alpine.data("lightboxGallery", (photos) => ({
    photos,
    active: null,
    imageLoaded: false,
    touchX: null,

    open(index) {
      this.show(index);
    },

    show(index) {
      if (index === this.active) return;
      this.imageLoaded = false;
      this.active = index;
      this.preload(index + 1);
      this.preload(index - 1);
    },

    preload(index) {
      const count = this.photos.length;
      new Image().src = this.photos[(index + count) % count].src;
    },

    close() {
      this.active = null;
    },

    current() {
      return this.active === null ? {} : this.photos[this.active];
    },

    prev() {
      if (this.active === null) return;
      this.show((this.active - 1 + this.photos.length) % this.photos.length);
    },

    next() {
      if (this.active === null) return;
      this.show((this.active + 1) % this.photos.length);
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
