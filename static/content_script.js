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

// 📌 Последняя сессия
let lastSeenId = null;
try {
  const session = JSON.parse(localStorage.getItem('last_session') || '{}');
  lastSeenId = session.itemId?.toString() || null;
} catch (err) {
  console.warn("❌ Ошибка разбора last_session:", err);
  localStorage.removeItem('last_session');
}

// 📌 Получаем избранное и начинаем загрузку жанра
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
        const anchorDiv = isLastSeen ? `<div id="scroll_target" style="height: 1px;"></div>` : '';

        let block = '';
        if (item.content_type === 'video') {
          block = `
            ${anchorDiv}
            <div class="video">
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
            ${anchorDiv}
            <div class="audio">
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
            ${anchorDiv}
            <div class="file">
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
              .catch(err => {
                console.error("Ошибка при обновлении избранного:", err);
                alert('Ошибка сети при обновлении избранного');
              });
          });
        }

        allCards.push({ ...item, genreId: genre.id });
      });

      localStorage.setItem('allCards', JSON.stringify(allCards));

      // ✅ Прокрутка к нужному элементу
      if (!lastSeenId) return;

      try {
        const observer = new MutationObserver((mutations, obs) => {
          const target = document.querySelector(`.fav_icon[data-id="${lastSeenId}"]`);
          if (target) {
            const card = target.closest('.video, .audio, .file');
            if (card) {
              const offset = card.getBoundingClientRect().top + window.scrollY;
              window.scrollTo({ top: offset - 80, behavior: 'smooth' });
              console.log("✅ Прокручено к карточке ID:", lastSeenId);
              localStorage.removeItem('last_session');
              obs.disconnect();
            }
          }
        });

        observer.observe(container, { childList: true, subtree: true });

        // 🕐 Доп. попытка через setTimeout
        setTimeout(() => {
          const el = document.querySelector(`.fav_icon[data-id="${lastSeenId}"]`);
          if (el) {
            const card = el.closest('.video, .audio, .file');
            if (card) {
              const offset = card.getBoundingClientRect().top + window.scrollY;
              window.scrollTo({ top: offset - 80, behavior: 'smooth' });
              localStorage.removeItem('last_session');
              console.log("⏱ Резервная прокрутка выполнена");
            }
          }
        }, 1500);
      } catch (e) {
        console.warn("❌ Ошибка scroll:", e);
        localStorage.removeItem('last_session');
      }
    })
    .catch(err => {
      console.error("Ошибка загрузки жанра:", err);
    });
}

// ✅ Сохраняем и переходим
function openAndRemember(item, genre) {
  localStorage.setItem('last_session', JSON.stringify({
    genreId: genre.id,
    genreTitle: genre.title,
    itemTitle: item.title,
    itemId: item.id,
    url: item.telegram_url
  }));

  Telegram.WebApp.close();
  setTimeout(() => {
    window.location.href = item.telegram_url;
  }, 400);
}
