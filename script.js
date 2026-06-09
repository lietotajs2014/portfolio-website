const filterButtons = document.querySelectorAll(".filter-button");
const workCards = document.querySelectorAll(".work-card[data-category]");
const languageButtons = document.querySelectorAll(".language-button");
const aboutTexts = document.querySelectorAll("[data-about-lang]");
const detailTitle = document.querySelector("[data-project-title]");
const detailGrid = document.querySelector("[data-project-grid]");

const galleryImages = {
  sports: "assets/temp-sports.svg",
  events: "assets/temp-events.svg",
  street: "assets/temp-street.svg",
  art: "assets/temp-art.svg",
  layout: "assets/temp-layout.svg",
  hero: "assets/portfolio-hero.png"
};

const buildGallery = (sources) => {
  const layout = ["is-wide", "is-tall", "is-square", "is-landscape", "is-tall", "is-square", "is-wide"];
  return sources.map((src, index) => ({
    src,
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

if (detailTitle && detailGrid) {
  const params = new URLSearchParams(window.location.search);
  const project = projectImages[params.get("project")] || projectImages.sports;

  document.title = `${project.title} | Lietotajs2014`;
  detailTitle.textContent = project.title;

  detailGrid.innerHTML = project.images
    .map((image) => `
      <figure class="detail-item ${image.layout}">
        <img src="${image.src}" alt="${project.title} temporary image" loading="lazy">
      </figure>
    `)
    .join("");
}
