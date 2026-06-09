const filterButtons = document.querySelectorAll(".filter-button");
const workCards = document.querySelectorAll(".work-card[data-category]");
const languageButtons = document.querySelectorAll(".language-button");
const aboutTexts = document.querySelectorAll("[data-about-lang]");
const detailTitle = document.querySelector("[data-project-title]");
const detailGrid = document.querySelector("[data-project-grid]");

const projectImages = {
  sports: {
    title: "Sports",
    images: ["assets/temp-sports.svg", "assets/portfolio-hero.png", "assets/temp-events.svg"]
  },
  events: {
    title: "Events",
    images: ["assets/temp-events.svg", "assets/portfolio-hero.png", "assets/temp-art.svg"]
  },
  street: {
    title: "Street",
    images: ["assets/temp-street.svg", "assets/portfolio-hero.png", "assets/temp-sports.svg"]
  },
  art: {
    title: "Art",
    images: ["assets/temp-art.svg", "assets/portfolio-hero.png", "assets/temp-layout.svg"]
  },
  "photo-manipulation": {
    title: "Photo Manipulation",
    images: ["assets/temp-art.svg", "assets/temp-street.svg", "assets/portfolio-hero.png"]
  },
  "poster-concepts": {
    title: "Poster Concepts",
    images: ["assets/temp-layout.svg", "assets/temp-events.svg", "assets/temp-art.svg"]
  },
  retouching: {
    title: "Retouching",
    images: ["assets/portfolio-hero.png", "assets/temp-sports.svg", "assets/temp-street.svg"]
  },
  "magazine-spreads": {
    title: "Magazine Spreads",
    images: ["assets/temp-layout.svg", "assets/temp-art.svg", "assets/temp-street.svg"]
  },
  "posters-flyers": {
    title: "Posters & Flyers",
    images: ["assets/temp-events.svg", "assets/temp-layout.svg", "assets/portfolio-hero.png"]
  },
  booklets: {
    title: "Booklets",
    images: ["assets/temp-layout.svg", "assets/temp-sports.svg", "assets/temp-art.svg"]
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
    .map((image) => `<img src="${image}" alt="${project.title} temporary image">`)
    .join("");
}
