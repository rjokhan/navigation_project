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

// 📌 Получаем из last_session title и genreTitle
const session = JSON.parse(localStorage.getItem('last_session') || '{}');
const lastTitle = session.itemTitle || null;
const lastGenre = session.genreTitle || null;

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

      let scrollAnchor = null;

      genre.items.forEach(item => {
        const isFavourited = userFavourites.includes(item.id);
        const favClass = isFavourited ? 'favourited' : 'not_favourited';
        const favIconHTML = `<div class="fav_icon ${favClass}" data-id="${item.id}" title="Добавить в избранное"></div>`;
        const openLink = `openAndRemember(${JSON.stringify(item)}, ${JSON.stringify(genre)})`;

        // Сравниваем item.title с lastTitle (сохраним совпадение)
        let cardIdAttr = '';
        if (
          lastTitle &&
          (item.title === lastTitle || item.title.trim() === lastTitle.trim())
        ) {
          cardIdAttr = 'id="scroll_target_card"';
          scrollAnchor = 'scroll_target_card';
        }

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

      // --- Скроллим к карточке по title, если нашли совпадение!
      if (scrollAnchor) {
        setTimeout(() => {
          const el = document.getElementById(scrollAnchor);
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            localStorage.removeItem('last_session');
          }
        }, 150); // небольшой таймаут на рендер
      }
    })
    .catch(() => {
      alert("Ошибка загрузки жанра");
    });
}

// 📌 Сохраняем сессию и переходим
function openAndRemember(item, genre) {
  localStorage.setItem('last_session', JSON.stringify({
    genreId: genre.id,
    genreTitle: genre.title,
    itemTitle: item.title,
    itemId: item.id
  }));
  setTimeout(() => {
    window.location.href = item.telegram_url;
    // Telegram.WebApp.close(); // если нужно, верни обратно
  }, 600);
}
