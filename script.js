const detailTitle = document.querySelector("[data-project-title]");
const detailGrid = document.querySelector("[data-project-grid]");
const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const lightboxCaption = document.querySelector("[data-lightbox-caption]");
const lightboxPrev = document.querySelector("[data-lightbox-prev]");
const lightboxNext = document.querySelector("[data-lightbox-next]");
const heroMarquee = document.querySelector("[data-hero-marquee]");
const portfolioReturnScrollKey = "olivera-portfolio-return-scroll-v1";
const portfolioRestoreNextKey = "olivera-portfolio-restore-next-v1";
let activeLightboxImages = [];
let activeLightboxIndex = -1;

const rememberPortfolioReturnPosition = () => {
  try {
    window.sessionStorage?.setItem(portfolioReturnScrollKey, JSON.stringify({
      scrollY: window.scrollY,
      timestamp: Date.now()
    }));
  } catch (_error) {
    // Navigation should still work when storage is unavailable.
  }
};

const markPortfolioReturnRequested = () => {
  try {
    window.sessionStorage?.setItem(portfolioRestoreNextKey, "1");
  } catch (_error) {
    // The title link still falls back to the portfolio section.
  }
};

const restorePortfolioReturnPosition = () => {
  if (!heroMarquee) {
    return;
  }

  try {
    if (window.sessionStorage?.getItem(portfolioRestoreNextKey) !== "1") {
      return;
    }

    window.sessionStorage.removeItem(portfolioRestoreNextKey);
    const storedPosition = JSON.parse(window.sessionStorage.getItem(portfolioReturnScrollKey) || "{}");
    const scrollY = Number(storedPosition.scrollY);

    if (!Number.isFinite(scrollY)) {
      return;
    }

    window.requestAnimationFrame(() => {
      window.scrollTo({ top: scrollY, behavior: "auto" });
    });
  } catch (_error) {
    window.sessionStorage?.removeItem(portfolioRestoreNextKey);
  }
};

const registerPortfolioOpen = () => {
  const storageKey = "olivera-portfolio-counted-v1";
  try {
    if (window.localStorage?.getItem(storageKey)) {
      return;
    }
    window.localStorage?.setItem(storageKey, new Date().toISOString());
  } catch (_error) {
    // If storage is blocked, still allow the public counter pixel to load.
  }

  const pixel = new Image(1, 1);
  pixel.referrerPolicy = "no-referrer";
  pixel.alt = "";
  pixel.src = "https://counterapi.com/pixel.gif?ns=olivera-tomasa-svana-portfolio&action=site-open&key=unique-device";
};

registerPortfolioOpen();

const galleryImages = {
  events: "assets/temp-events.svg",
  street: "assets/temp-street.svg",
  art: "assets/temp-art.svg",
  layout: "assets/temp-layout.svg",
  hero: "assets/portfolio-hero.png"
};

const tempCaptions = [
  "Pagaidu paraksts šim attēlam.",
  "Īsa piezīme par mirkli, apstrādi vai maketu.",
  "Piemēra teksts zem attēla.",
  "Vieta kontekstam, datumam vai projekta detaļai.",
  "Paraksta priekšskatījums palielinātajā skatā.",
  "Īss apraksts portfolio režģim.",
  "Vēlāk aizvieto šo ar īsto tekstu."
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
    videoUrl: typeof item === "string" ? "" : item.videoUrl,
    featured: typeof item === "string" ? false : Boolean(item.featured),
    showcase: typeof item === "string" ? false : Boolean(item.showcase),
    layout: typeof item !== "string" && item.featured ? "is-featured" : layout[index % layout.length]
  }));
};

const defaultVideoFrames = [];

const projectImages = {
  nature: {
    title: "Daba",
    images: []
  },
  events: {
    title: "Pasākumi",
    images: []
  },
  street: {
    title: "Street",
    images: []
  },
  art: {
    title: "Māksla",
    images: []
  },
  portraits: {
    title: "Portreti",
    images: []
  },
  photoshop: {
    title: "Photoshop",
    images: []
  },
  "gimnazijas-laiki": {
    title: "Ğimnāzijas Laiki",
    images: []
  },
  "dzejas-krajums": {
    title: "Dzejas krājums",
    images: []
  },
  "video-editing": {
    title: "Video montēšana",
    titleIcon: "assets/premiere.png",
    titleIconAlt: "Premiere Pro",
    images: []
  }
};

const importedItems = window.PORTFOLIO_ITEMS || {};
const videoShowcase = document.querySelector("[data-video-showcase]");
let heroScrollFrame = null;

const startHeroGridScroll = () => {
  const track = heroMarquee?.querySelector(".hero-grid-track");

  if (!track) {
    return;
  }

  if (heroScrollFrame) {
    window.cancelAnimationFrame(heroScrollFrame);
  }

  let offset = 0;
  let previousTime = window.performance.now();
  const speed = 18;

  const step = (currentTime) => {
    const distance = Math.max(1, track.scrollWidth / 2);
    const deltaSeconds = (currentTime - previousTime) / 1000;
    offset = (offset + (speed * deltaSeconds)) % distance;
    track.style.transform = `translate3d(${-offset}px, 0, 0)`;
    previousTime = currentTime;
    heroScrollFrame = window.requestAnimationFrame(step);
  };

  heroScrollFrame = window.requestAnimationFrame(step);
};

const renderHeroMarquee = () => {
  if (!heroMarquee) {
    return;
  }

  const submittedImages = Object.values(importedItems)
    .flatMap((items) => Array.isArray(items) ? items : [])
    .map((item) => item?.src)
    .filter(Boolean);
  const uniqueImages = Array.from(new Set(submittedImages));
  if (uniqueImages.length === 0) {
    heroMarquee.innerHTML = "";
    return;
  }

  const version = `${uniqueImages.length}-${uniqueImages.join("|").length}`;
  const marqueeSrc = `assets/hero-marquee.jpg?v=${escapeHtml(version)}`;

  heroMarquee.innerHTML = `
    <div class="hero-grid-track">
      <img class="hero-marquee-strip" src="${marqueeSrc}" alt="" decoding="async" fetchpriority="high">
      <img class="hero-marquee-strip" src="${marqueeSrc}" alt="" aria-hidden="true" decoding="async">
    </div>
  `;

  startHeroGridScroll();
};

renderHeroMarquee();

Object.entries(importedItems).forEach(([projectKey, items]) => {
  if (!Array.isArray(items) || items.length === 0) {
    return;
  }

  if (projectImages[projectKey]) {
    projectImages[projectKey].images = buildGallery(items);
  }
});

const updateCardPreview = (projectKey, selector) => {
  const items = projectImages[projectKey]?.images || [];
  const track = document.querySelector(`${selector} .slideshow-track`);

  if (!track || items.length === 0) {
    return;
  }

  const previewLimit = projectKey === "video-editing" ? 5 : 3;
  const showcaseImages = items.filter((item) => item.showcase);
  const sourceImages = showcaseImages.length > 0 ? showcaseImages : items.filter((item) => item.featured);
  const previewImages = sourceImages.slice(0, previewLimit);

  if (previewImages.length === 0) {
    track.innerHTML = "";
    return;
  }

  while (previewImages.length < previewLimit) {
    previewImages.push(previewImages[previewImages.length - 1]);
  }

  track.style.setProperty("--slide-count", previewImages.length);
  track.style.setProperty("--slide-duration", `${previewImages.length * 4}s`);
  track.innerHTML = previewImages
    .map((item, index) => `<img src="${escapeHtml(item.src)}" alt="" style="--slide-delay: ${index * 4}s;">`)
    .join("");
};

const applyProjectExternalLink = (projectKey, selector) => {
  const card = document.querySelector(selector);
  const items = projectImages[projectKey]?.images || [];
  const externalUrl = (
    items.find((item) => item.showcase && item.videoUrl)
    || items.find((item) => item.videoUrl)
  )?.videoUrl;

  if (!card || !externalUrl) {
    return;
  }

  card.href = externalUrl;
  card.target = "_blank";
  card.rel = "noreferrer";
};

const renderVideoShowcase = () => {
  if (!videoShowcase) {
    return;
  }

  const projectItems = projectImages["video-editing"]?.images || [];
  const items = projectItems;
  const groups = new Map();

  items
    .filter((item) => item.videoUrl)
    .forEach((item) => {
      if (!groups.has(item.videoUrl)) {
        groups.set(item.videoUrl, []);
      }
      groups.get(item.videoUrl).push(item);
    });

  videoShowcase.innerHTML = Array.from(groups.entries())
    .map(([videoUrl, frames], index) => {
      const previewImages = frames.slice(0, 5);
      while (previewImages.length > 0 && previewImages.length < 3) {
        previewImages.push(previewImages[previewImages.length - 1]);
      }

      const title = frames.find((frame) => frame.caption)?.caption || `Video ${index + 1}`;
      const slideCount = previewImages.length || 1;
      const images = previewImages
        .map((frame, frameIndex) => `<img src="${escapeHtml(frame.src)}" alt="" style="--slide-delay: ${frameIndex * 4}s;">`)
        .join("");

      return `
        <a class="work-card" href="${escapeHtml(videoUrl)}" target="_blank" rel="noreferrer">
          <div class="work-image slideshow">
            <div class="slideshow-track" style="--slide-count: ${slideCount}; --slide-duration: ${slideCount * 4}s;">
              ${images}
            </div>
          </div>
          <div class="work-info">
            <h3>${escapeHtml(title)}</h3>
          </div>
        </a>
      `;
    })
    .join("");
};

const layoutDetailGrid = () => {
  if (!detailGrid) {
    return;
  }

  const styles = window.getComputedStyle(detailGrid);
  const rowHeight = parseFloat(styles.getPropertyValue("grid-auto-rows")) || 8;
  const rowGap = parseFloat(styles.getPropertyValue("row-gap")) || 0;

  detailGrid.querySelectorAll(".detail-item").forEach((item) => {
    const image = item.querySelector("img");
    if (!image || !image.complete || image.naturalHeight === 0) {
      return;
    }

    item.style.gridRowEnd = "auto";
    const itemHeight = item.getBoundingClientRect().height;
    const span = Math.max(1, Math.ceil((itemHeight + rowGap) / (rowHeight + rowGap)));
    item.style.gridRowEnd = `span ${span}`;
    item.classList.add("is-laid-out");
  });
};

let layoutFrame = null;
const scheduleDetailGridLayout = () => {
  if (layoutFrame) {
    window.cancelAnimationFrame(layoutFrame);
  }

  layoutFrame = window.requestAnimationFrame(() => {
    layoutFrame = null;
    layoutDetailGrid();
  });
};

updateCardPreview("nature", '[href="work.html?project=nature"]');
updateCardPreview("events", '[href="work.html?project=events"]');
updateCardPreview("street", '[href="work.html?project=street"]');
updateCardPreview("art", '[href="work.html?project=art"]');
updateCardPreview("portraits", '[href="work.html?project=portraits"]');
updateCardPreview("photoshop", '[href="work.html?project=photoshop"]');
updateCardPreview("gimnazijas-laiki", '[href="work.html?project=gimnazijas-laiki"]');
applyProjectExternalLink("gimnazijas-laiki", '[href="work.html?project=gimnazijas-laiki"]');
updateCardPreview("dzejas-krajums", '[href="work.html?project=dzejas-krajums"]');
applyProjectExternalLink("dzejas-krajums", '[href="work.html?project=dzejas-krajums"]');
renderVideoShowcase();

document.querySelector("[data-portfolio-return-home]")?.addEventListener("click", markPortfolioReturnRequested);

document.querySelectorAll('a[href^="work.html?project="]').forEach((link) => {
  link.addEventListener("click", () => {
    if (link.getAttribute("href")?.startsWith("work.html?project=")) {
      rememberPortfolioReturnPosition();
    }
  });
});

const updateLightboxNav = () => {
  const hasMultipleImages = activeLightboxImages.length > 1;

  if (lightboxPrev) {
    lightboxPrev.hidden = !hasMultipleImages;
  }

  if (lightboxNext) {
    lightboxNext.hidden = !hasMultipleImages;
  }
};

const showLightboxImage = (index) => {
  if (!lightbox || !lightboxImage || !lightboxCaption || activeLightboxImages.length === 0) {
    return;
  }

  const normalizedIndex = (index + activeLightboxImages.length) % activeLightboxImages.length;
  const image = activeLightboxImages[normalizedIndex];

  activeLightboxIndex = normalizedIndex;
  lightboxImage.src = image.src;
  lightboxImage.alt = image.caption || "Portfolio attēls";
  lightboxCaption.textContent = image.caption || "";
  updateLightboxNav();

  if (!lightbox.open) {
    lightbox.showModal();
  }
};

if (detailTitle && detailGrid) {
  const params = new URLSearchParams(window.location.search);
  const project = projectImages[params.get("project")] || projectImages.events;
  activeLightboxImages = project.images.filter((image) => !image.videoUrl);

  document.title = `${project.title} | Olivera Švāna portfolio`;
  if (project.titleIcon) {
    detailTitle.innerHTML = `<img class="app-icon-title" src="${escapeHtml(project.titleIcon)}" alt="${escapeHtml(project.titleIconAlt || project.title)}">`;
  } else {
    detailTitle.textContent = project.title;
  }

  detailGrid.innerHTML = project.images
    .map((image) => {
      const imageIndex = activeLightboxImages.indexOf(image);

      return `
      <figure class="detail-item ${image.layout}">
        <button class="detail-image-button" type="button" data-image-index="${imageIndex}" data-image-src="${escapeHtml(image.src)}" data-image-caption="${escapeHtml(image.caption)}" data-video-url="${escapeHtml(image.videoUrl)}">
          <img src="${escapeHtml(image.src)}" alt="${escapeHtml(project.title)} attēls" loading="lazy">
        </button>
        ${image.caption ? `<figcaption>${escapeHtml(image.caption)}</figcaption>` : ""}
      </figure>
    `;
    })
    .join("");

  detailGrid.querySelectorAll("img").forEach((image) => {
    if (image.complete) {
      scheduleDetailGridLayout();
      return;
    }

    image.addEventListener("load", scheduleDetailGridLayout);
    image.addEventListener("error", scheduleDetailGridLayout);
  });

  window.addEventListener("resize", scheduleDetailGridLayout);
  scheduleDetailGridLayout();
}

document.querySelectorAll("[data-image-src]").forEach((button) => {
  button.addEventListener("click", () => {
    if (button.dataset.videoUrl) {
      window.open(button.dataset.videoUrl, "_blank", "noopener");
      return;
    }

    const imageIndex = Number(button.dataset.imageIndex);
    if (!Number.isFinite(imageIndex) || imageIndex < 0) {
      return;
    }

    showLightboxImage(imageIndex);
  });
});

lightboxPrev?.addEventListener("click", () => {
  showLightboxImage(activeLightboxIndex - 1);
});

lightboxNext?.addEventListener("click", () => {
  showLightboxImage(activeLightboxIndex + 1);
});

lightbox?.addEventListener("click", (event) => {
  if (!event.target.closest("[data-lightbox-frame]")) {
    lightbox.close();
  }
});

document.addEventListener("keydown", (event) => {
  if (!lightbox?.open || activeLightboxImages.length < 2) {
    return;
  }

  if (event.key === "ArrowLeft") {
    event.preventDefault();
    showLightboxImage(activeLightboxIndex - 1);
  }

  if (event.key === "ArrowRight") {
    event.preventDefault();
    showLightboxImage(activeLightboxIndex + 1);
  }
});

restorePortfolioReturnPosition();
