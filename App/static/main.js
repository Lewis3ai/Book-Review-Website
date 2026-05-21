/* =============================================
   BookShelf — Main JavaScript
   ============================================= */

(function () {
  'use strict';

  // ── Helpers ──────────────────────────────────
  function stars(rating) {
    let html = '';
    for (let i = 1; i <= 5; i++) {
      html += `<span style="color:${i <= rating ? '#F5A623' : '#D1CFC6'}">★</span>`;
    }
    return html;
  }

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  // ── Reviews data ─────────────────────────────
  let reviewsData = {};
  const dataEl = document.getElementById('reviewsData');
  if (dataEl) {
    try { reviewsData = JSON.parse(dataEl.textContent); } catch (e) { /* ignore */ }
  }

  // ── Search ───────────────────────────────────
  const searchInput = document.getElementById('bookSearch');
  const bookGrid    = document.getElementById('bookGrid');
  const noResults   = document.getElementById('noResults');

  if (searchInput && bookGrid) {
    searchInput.addEventListener('input', function () {
      const q = this.value.trim().toLowerCase();
      const cards = bookGrid.querySelectorAll('.book-card');
      let visible = 0;

      cards.forEach(function (card) {
        const haystack = card.dataset.search || '';
        const show = !q || haystack.includes(q);
        card.style.display = show ? '' : 'none';
        if (show) visible++;
      });

      if (noResults) {
        noResults.classList.toggle('d-none', visible > 0);
      }
    });
  }

  // ── Check if we should open a book on page load ──
  function getUrlParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  // ── Modal logic ──────────────────────────────
  const bookModal = document.getElementById('bookModal');
  if (!bookModal) return;

  const modalImage       = document.getElementById('modalImage');
  const modalPlaceholder = document.getElementById('modalPlaceholder');
  const modalInitial     = document.getElementById('modalInitial');
  const modalTitle       = document.getElementById('modalTitle');
  const modalAuthor      = document.getElementById('modalAuthor');
  const modalMeta        = document.getElementById('modalMeta');
  const modalRating      = document.getElementById('modalRating');
  const reviewForm       = document.getElementById('reviewForm');
  const reviewsList      = document.getElementById('reviewsList');
  const starInput        = document.getElementById('starInput');
  const ratingInput      = document.getElementById('ratingInput');
  const ratingError      = document.getElementById('ratingError');
  const reviewText       = document.getElementById('reviewText');
  const textError        = document.getElementById('textError');
  const charCount        = document.getElementById('charCount');

  let currentIsbn = null;

  // ── Open modal when card clicked ─────────────
  document.querySelectorAll('.book-card').forEach(function (card) {
    card.addEventListener('click', function () {
      openModal(card);
    });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal(card);
      }
    });
  });

  function openModal(card) {
    const isbn      = card.dataset.isbn;
    const title     = card.dataset.title;
    const author    = card.dataset.author;
    const year      = card.dataset.year;
    const publisher = card.dataset.publisher;
    const image     = card.dataset.image;
    const avg       = card.dataset.avg;
    const count     = parseInt(card.dataset.count, 10) || 0;

    currentIsbn = isbn;

    // Cover image
    if (image) {
      modalImage.src = image;
      modalImage.alt = title + ' cover';
      modalImage.style.display = 'block';
      modalImage.onerror = function () {
        modalImage.style.display = 'none';
        modalPlaceholder.classList.remove('d-none');
        modalInitial.textContent = title.charAt(0).toUpperCase();
      };
      modalPlaceholder.classList.add('d-none');
    } else {
      modalImage.style.display = 'none';
      modalPlaceholder.classList.remove('d-none');
      modalInitial.textContent = title.charAt(0).toUpperCase();
    }

    // Text info
    modalTitle.textContent  = title;
    modalAuthor.textContent = author;

    const metaParts = [];
    if (year)      metaParts.push(year);
    if (publisher) metaParts.push(publisher);
    modalMeta.textContent = metaParts.join(' · ');

    // Overall rating
    if (avg) {
      modalRating.innerHTML =
        `<span class="modal-stars">${stars(Math.round(parseFloat(avg)))}</span>` +
        `<strong>${avg}</strong>` +
        `<span class="text-muted ms-1 small">(${count} review${count !== 1 ? 's' : ''})</span>`;
    } else {
      modalRating.innerHTML = '<span class="text-muted small">No ratings yet — be the first!</span>';
    }

    // Review form action
    reviewForm.action = '/add-review/' + isbn;

    // Reset form
    resetForm();

    // Load reviews
    renderReviews(isbn);
  }

  // ── Render existing reviews ───────────────────
  function renderReviews(isbn) {
    const list = reviewsData[isbn] || [];
    if (!reviewsList) return;

    if (list.length === 0) {
      reviewsList.innerHTML = '<p class="no-reviews">No reviews yet. Be the first to share your thoughts!</p>';
      return;
    }

    reviewsList.innerHTML = list.map(function (r) {
      return `
        <div class="review-item">
          <div class="review-header">
            <span class="review-username">👤 ${escapeHtml(r.username)}</span>
            <span class="review-stars">${stars(r.rating)}</span>
          </div>
          <p class="review-text">${escapeHtml(r.text)}</p>
        </div>
      `;
    }).join('');
  }

  // ── Reset form state ─────────────────────────
  function resetForm() {
    if (reviewForm) reviewForm.reset();
    ratingInput.value = '';
    if (charCount) charCount.textContent = '0';
    document.querySelectorAll('.star-btn').forEach(function (s) {
      s.classList.remove('selected', 'hovered');
    });
    if (ratingError) ratingError.classList.add('d-none');
    if (textError)   textError.classList.add('d-none');
  }

  // ── Reset form on modal close ─────────────────
  bookModal.addEventListener('hidden.bs.modal', resetForm);

  // ── Star rating interaction ───────────────────
  if (starInput) {
    const starBtns = starInput.querySelectorAll('.star-btn');

    starBtns.forEach(function (btn) {
      btn.addEventListener('mouseenter', function () {
        const val = parseInt(btn.dataset.value, 10);
        starBtns.forEach(function (s) {
          s.classList.toggle('hovered', parseInt(s.dataset.value, 10) <= val);
        });
      });

      btn.addEventListener('mouseleave', function () {
        starBtns.forEach(function (s) { s.classList.remove('hovered'); });
      });

      btn.addEventListener('click', function () {
        const val = parseInt(btn.dataset.value, 10);
        ratingInput.value = val;
        starBtns.forEach(function (s) {
          s.classList.toggle('selected', parseInt(s.dataset.value, 10) <= val);
          s.setAttribute('aria-checked', parseInt(s.dataset.value, 10) === val ? 'true' : 'false');
        });
        if (ratingError) ratingError.classList.add('d-none');
      });

      btn.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          btn.click();
        }
      });
    });
  }

  // ── Character counter ─────────────────────────
  if (reviewText && charCount) {
    reviewText.addEventListener('input', function () {
      charCount.textContent = this.value.length;
    });
  }

  // ── Form validation before submit ────────────
  if (reviewForm) {
    reviewForm.addEventListener('submit', function (e) {
      let valid = true;

      if (!ratingInput.value) {
        e.preventDefault();
        if (ratingError) ratingError.classList.remove('d-none');
        valid = false;
      }

      const text = reviewText ? reviewText.value.trim() : '';
      if (!text) {
        e.preventDefault();
        if (textError) textError.classList.remove('d-none');
        valid = false;
      }

      return valid;
    });
  }

  // ── Auto-open modal if ?book= param present ───
  const bookParam = getUrlParam('book');
  if (bookParam) {
    const targetCard = document.querySelector(`.book-card[data-isbn="${CSS.escape(bookParam)}"]`);
    if (targetCard) {
      const bsModal = new bootstrap.Modal(bookModal);
      openModal(targetCard);
      bsModal.show();
      // Clean URL without reload
      const url = new URL(window.location.href);
      url.searchParams.delete('book');
      window.history.replaceState({}, '', url.toString());
    }
  }

})();


