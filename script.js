const filterButtons = document.querySelectorAll(".filter-button");
const workCards = document.querySelectorAll(".work-card");
const languageButtons = document.querySelectorAll(".language-button");
const translatableItems = document.querySelectorAll("[data-i18n]");

const translations = {
  en: {
    navPhotography: "Photography",
    navAbout: "About",
    heroEyebrow: "Photography / design",
    heroTitle: "Portfolio",
    viewWork: "View work",
    contact: "Contact",
    photography: "Photography",
    categories: "Categories",
    all: "All",
    sports: "Sports",
    events: "Events",
    street: "Street",
    art: "Art",
    projects: "Projects",
    photoManipulation: "Photo Manipulation",
    posterConcepts: "Poster Concepts",
    retouching: "Retouching",
    editorial: "Editorial",
    magazineSpreads: "Magazine Spreads",
    print: "Print",
    postersFlyers: "Posters & Flyers",
    publication: "Publication",
    booklets: "Booklets",
    aboutTitle: "Photography / Photoshop / InDesign",
    backTop: "Back to top"
  },
  lv: {
    navPhotography: "Fotogrāfija",
    navAbout: "Par mani",
    heroEyebrow: "Fotogrāfija / dizains",
    heroTitle: "Portfolio",
    viewWork: "Darbi",
    contact: "Kontakti",
    photography: "Fotogrāfija",
    categories: "Kategorijas",
    all: "Visi",
    sports: "Sports",
    events: "Pasākumi",
    street: "Iela",
    art: "Māksla",
    projects: "Projekti",
    photoManipulation: "Foto manipulācijas",
    posterConcepts: "Plakāti",
    retouching: "Retuša",
    editorial: "Redakcija",
    magazineSpreads: "Žurnālu atvērumi",
    print: "Druka",
    postersFlyers: "Plakāti un skrejlapas",
    publication: "Publikācija",
    booklets: "Bukleti",
    aboutTitle: "Fotogrāfija / Photoshop / InDesign",
    backTop: "Uz augšu"
  }
};

const setLanguage = (language) => {
  const dictionary = translations[language] || translations.en;

  document.documentElement.lang = language;

  translatableItems.forEach((item) => {
    item.textContent = dictionary[item.dataset.i18n];
  });

  languageButtons.forEach((button) => {
    const isActive = button.dataset.lang === language;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });

  localStorage.setItem("portfolio-language", language);
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
  button.addEventListener("click", () => setLanguage(button.dataset.lang));
});

setLanguage(localStorage.getItem("portfolio-language") || "en");
