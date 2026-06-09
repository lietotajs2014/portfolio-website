const filterButtons = document.querySelectorAll(".filter-button");
const workCards = document.querySelectorAll(".work-card[data-category]");
const languageButtons = document.querySelectorAll(".language-button");
const aboutTexts = document.querySelectorAll("[data-about-lang]");
const detailTitle = document.querySelector("[data-project-title]");
const detailGrid = document.querySelector("[data-project-grid]");
const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const lightboxCaption = document.querySelector("[data-lightbox-caption]");
const lightboxClose = document.querySelector("[data-lightbox-close]");

const galleryImages = {
  sports: "assets/temp-sports.svg",
  events: "assets/temp-events.svg",
  street: "assets/temp-street.svg",
  art: "assets/temp-art.svg",
  layout: "assets/temp-layout.svg",
  hero: "assets/portfolio-hero.png"
};

const tempCaptions = [
  "Temporary caption for this image.",
  "Short note about the moment, edit, or layout.",
  "Example text shown under the image.",
  "A place for context, date, or project detail.",
  "Caption preview for the enlarged view.",
  "Small description for the portfolio grid.",
  "Replace this with your final text later."
];

const escapeHtml = (value) => String(value || "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const buildGallery = (sources) => {
  const layout = ["is-wide", "is-tall", "is-square", "is-landscape", "is-tall", "is-square", "is-wide"];
  return sources.map((item, index) => ({
    src: typeof item === "string" ? item : item.src,
    caption: typeof item === "string" ? tempCaptions[index % tempCaptions.length] : item.caption,
    layout: layout[index % layout.length]
  }));
};

const projectImages = {
  sports: {
    title: "Sports",
    images: buildGallery([
      galleryImages.sports,
      galleryImages.hero,
      galleryImages.events,
      galleryImages.street,
      galleryImages.art,
      galleryImages.layout,
      galleryImages.sports
    ])
  },
  events: {
    title: "Events",
    images: buildGallery([
      galleryImages.events,
      galleryImages.hero,
      galleryImages.art,
      galleryImages.layout,
      galleryImages.street,
      galleryImages.events,
      galleryImages.sports
    ])
  },
  street: {
    title: "Street",
    images: buildGallery([
      galleryImages.street,
      galleryImages.hero,
      galleryImages.sports,
      galleryImages.art,
      galleryImages.layout,
      galleryImages.events,
      galleryImages.street
    ])
  },
  art: {
    title: "Art",
    images: buildGallery([
      galleryImages.art,
      galleryImages.hero,
      galleryImages.layout,
      galleryImages.street,
      galleryImages.events,
      galleryImages.sports,
      galleryImages.art
    ])
  },
  "photo-manipulation": {
    title: "Photo Manipulation",
    images: buildGallery([
      galleryImages.art,
      galleryImages.street,
      galleryImages.hero,
      galleryImages.events,
      galleryImages.layout,
      galleryImages.sports,
      galleryImages.art
    ])
  },
  "poster-concepts": {
    title: "Poster Concepts",
    images: buildGallery([
      galleryImages.layout,
      galleryImages.events,
      galleryImages.art,
      galleryImages.hero,
      galleryImages.street,
      galleryImages.layout,
      galleryImages.sports
    ])
  },
  retouching: {
    title: "Retouching",
    images: buildGallery([
      galleryImages.hero,
      galleryImages.sports,
      galleryImages.street,
      galleryImages.art,
      galleryImages.events,
      galleryImages.layout,
      galleryImages.hero
    ])
  },
  "gimnazijas-laiki": {
    title: "Ğimnāzijas Laiki",
    images: buildGallery([
      galleryImages.layout,
      galleryImages.art,
      galleryImages.street,
      galleryImages.hero,
      galleryImages.events,
      galleryImages.layout,
      galleryImages.sports
    ])
  },
  "dzejas-krajums": {
    title: "Dzejas krājums",
    images: buildGallery([
      galleryImages.layout,
      galleryImages.sports,
      galleryImages.art,
      galleryImages.street,
      galleryImages.hero,
      galleryImages.events,
      galleryImages.layout
    ])
  }
};

const importedItems = window.PORTFOLIO_ITEMS || {};

Object.entries(importedItems).forEach(([projectKey, items]) => {
  if (!Array.isArray(items) || items.length === 0) {
    return;
  }

  if (projectImages[projectKey]) {
    projectImages[projectKey].images = buildGallery(items);
  }
});

const updateCardPreview = (projectKey, selector) => {
  const items = importedItems[projectKey];
  const track = document.querySelector(`${selector} .slideshow-track`);

  if (!track || !Array.isArray(items) || items.length === 0) {
    return;
  }

  const previewImages = items.slice(0, 3);
  while (previewImages.length < 3) {
    previewImages.push(previewImages[previewImages.length - 1]);
  }

  track.innerHTML = previewImages
    .map((item) => `<img src="${item.src}" alt="">`)
    .join("");
};

const setAboutLanguage = (language) => {
  aboutTexts.forEach((item) => {
    item.classList.toggle("is-hidden", item.dataset.aboutLang !== language);
  });

  languageButtons.forEach((button) => {
    const isActive = button.dataset.lang === language;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });

  localStorage.setItem("portfolio-about-language", language);
};

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const selectedCategory = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");

    workCards.forEach((card) => {
      const shouldShow = selectedCategory === "all" || card.dataset.category === selectedCategory;
      card.classList.toggle("is-hidden", !shouldShow);
    });
  });
});

languageButtons.forEach((button) => {
  button.addEventListener("click", () => setAboutLanguage(button.dataset.lang));
});

if (languageButtons.length > 0) {
  setAboutLanguage(localStorage.getItem("portfolio-about-language") || "en");
}

updateCardPreview("sports", '[href="work.html?project=sports"]');
updateCardPreview("events", '[href="work.html?project=events"]');
updateCardPreview("street", '[href="work.html?project=street"]');
updateCardPreview("art", '[href="work.html?project=art"]');
updateCardPreview("photo-manipulation", '[href="work.html?project=photo-manipulation"]');
updateCardPreview("poster-concepts", '[href="work.html?project=poster-concepts"]');
updateCardPreview("retouching", '[href="work.html?project=retouching"]');
updateCardPreview("gimnazijas-laiki", '[href="work.html?project=gimnazijas-laiki"]');
updateCardPreview("dzejas-krajums", '[href="work.html?project=dzejas-krajums"]');

if (detailTitle && detailGrid) {
  const params = new URLSearchParams(window.location.search);
  const project = projectImages[params.get("project")] || projectImages.sports;

  document.title = `${project.title} | Lietotajs2014`;
  detailTitle.textContent = project.title;

  detailGrid.innerHTML = project.images
    .map((image) => `
      <figure class="detail-item ${image.layout}">
        <button class="detail-image-button" type="button" data-image-src="${escapeHtml(image.src)}" data-image-caption="${escapeHtml(image.caption)}">
          <img src="${escapeHtml(image.src)}" alt="${escapeHtml(project.title)} image" loading="lazy">
        </button>
        ${image.caption ? `<figcaption>${escapeHtml(image.caption)}</figcaption>` : ""}
      </figure>
    `)
    .join("");
}

document.querySelectorAll("[data-image-src]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!lightbox || !lightboxImage || !lightboxCaption) {
      return;
    }

    lightboxImage.src = button.dataset.imageSrc;
    lightboxImage.alt = button.dataset.imageCaption || "Portfolio image";
    lightboxCaption.textContent = button.dataset.imageCaption || "";
    lightbox.showModal();
  });
});

lightboxClose?.addEventListener("click", () => lightbox.close());

lightbox?.addEventListener("click", (event) => {
  if (event.target === lightbox) {
    lightbox.close();
  }
});
