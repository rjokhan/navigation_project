// 📌 Получение параметров из URL
const params = new URLSearchParams(window.location.search);
const genreId = params.get("genre_id");
const genreTitleRaw = params.get("genre_title");
const genreTitle = genreTitleRaw ? genreTitleRaw.trim().replace(/^A\s+/i, '') : '';
document.getElementById("genre-title").textContent = genreTitle || '';

// 📌 Telegram ID
const telegramId = localStorage.getItem('telegram_id');
if (!telegramId) {
  alert("Ошибка: Telegram ID не найден. Пожалуйста, войдите.");
  throw new Error('Telegram ID не найден');
}

// 📌 Получение ID последней карточки
let lastSeenId = localStorage.getItem('last_seen_id')?.toString() || null;

// 📌 Получаем избранное и запускаем загрузку жанра
let userFavourites = [];
fetch(`/api/favourites/?telegram_id=${telegramId}`)
  .then(res => res.json())
  .then(data => {
    userFavourites = data.favourites || [];
    loadGenre();
  })
  .catch(() => {
    userFavourites = [];
    loadGenre();
  });

function loadGenre() {
  fetch(`/api/genres/`)
    .then(response => response.json())
    .then(data => {
      const genre = data.find(g => g.id == genreId);
      if (!genre) return;

      const container = document.querySelector('.content_body');
      container.innerHTML = '';
      const allCards = [];

      genre.items.forEach(item => {
        const isFavourited = userFavourites.includes(item.id);
        const favClass = isFavourited ? 'favourited' : 'not_favourited';
        const favIconHTML = `<div class="fav_icon ${favClass}" data-id="${item.id}" title="Добавить в избранное"></div>`;
        const openLink = `openAndRemember(${JSON.stringify(item)}, ${JSON.stringify(genre)})`;
        const isLastSeen = item.id.toString() === lastSeenId;
        const cardIdAttr = isLastSeen ? 'id="scroll_target"' : '';

        let block = '';
        if (item.content_type === 'video') {
          block = `
            <div class="video" ${cardIdAttr}>
              <div class="video_thumbnail" onclick="${openLink}">
                <img src="${item.thumbnail}" alt="video_thumbnail">
                <div class="video_duration">${item.duration}</div>
              </div>
              ${favIconHTML}
              <div class="video_info">
                <div class="title">${item.title}</div>
                <div class="subtitle">${item.subtitle || ''}</div>
              </div>
            </div>
          `;
        } else if (item.content_type === 'audio') {
          block = `
            <div class="audio" ${cardIdAttr}>
              <div class="audio_menu" onclick="${openLink}">
                <div class="static_icon"><img src="/static/images/audio_icon.png"></div>
                <div class="audio_duration">${item.duration}</div>
              </div>
              ${favIconHTML}
              <div class="audio_info">
                <div class="title">${item.title}</div>
                <div class="subtitle">${item.subtitle || ''}</div>
              </div>
            </div>
          `;
        } else if (item.content_type === 'file') {
          block = `
            <div class="file" ${cardIdAttr}>
              <div class="file_menu" onclick="${openLink}">
                <div class="static_icon"><img src="/static/images/file_icon.png"></div>
                <div class="file_duration">${item.duration}</div>
              </div>
              ${favIconHTML}
              <div class="file_info">
                <div class="title">${item.title}</div>
                <div class="subtitle">${item.subtitle || ''}</div>
              </div>
            </div>
          `;
        }

        container.insertAdjacentHTML('beforeend', block);
        const favIcon = container.lastElementChild.querySelector('.fav_icon');

        if (favIcon) {
          favIcon.addEventListener('click', (e) => {
            e.stopPropagation();
            const isFavouritedNow = favIcon.classList.contains('favourited');
            const url = isFavouritedNow
              ? `/api/favourites/remove/${item.id}/`
              : `/api/favourites/add/${item.id}/`;

            fetch(url, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ telegram_id: telegramId })
            })
              .then(res => res.json())
              .then(data => {
                if (data.status === 'added') {
                  favIcon.classList.remove('not_favourited');
                  favIcon.classList.add('favourited');
                } else if (data.status === 'removed') {
                  favIcon.classList.remove('favourited');
                  favIcon.classList.add('not_favourited');
                } else {
                  alert('Ошибка обновления избранного');
                }
              })
              .catch(() => {
                alert('Ошибка сети при обновлении избранного');
              });
          });
        }

        allCards.push({ ...item, genreId: genre.id });
      });

      localStorage.setItem('allCards', JSON.stringify(allCards));

      // ✅ Прокрутка к нужной карточке
      if (!lastSeenId) return;

      const observer = new MutationObserver(() => {
        const target = document.querySelector('#scroll_target');
        if (target) {
          const offset = target.getBoundingClientRect().top + window.scrollY;
          window.scrollTo({ top: offset - 80, behavior: 'smooth' });
          localStorage.removeItem('last_seen_id');
          observer.disconnect();
        }
      });

      observer.observe(container, { childList: true, subtree: true });

      // 🔁 Резервная попытка (если observer не сработал)
      setTimeout(() => {
        const target = document.querySelector('#scroll_target');
        if (target) {
          const offset = target.getBoundingClientRect().top + window.scrollY;
          window.scrollTo({ top: offset - 80, behavior: 'smooth' });
          localStorage.removeItem('last_seen_id');
        }
      }, 2000);
    })
    .catch(() => {
      alert("Ошибка загрузки жанра");
    });
}

// 📌 Сохраняем ID и переходим
function openAndRemember(item, genre) {
  localStorage.setItem('last_seen_id', item.id.toString());
  Telegram.WebApp.close();
  setTimeout(() => {
    window.location.href = item.telegram_url;
  }, 400);
}
