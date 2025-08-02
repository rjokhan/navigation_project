const params = new URLSearchParams(window.location.search);
const genreId = params.get("genre_id");
const genreTitleRaw = params.get("genre_title");

// Убираем лишнее "A" и пробелы, оставляем только название жанра
const genreTitle = genreTitleRaw
  ? genreTitleRaw.trim().replace(/^A\s+/i, '')
  : '';

document.getElementById("genre-title").textContent = genreTitle || '';

const telegramId = localStorage.getItem('telegram_id');
if (!telegramId) {
  alert("Ошибка: Telegram ID не найден. Пожалуйста, войдите.");
  throw new Error('Telegram ID не найден');
}

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

        let block = '';
        if (item.content_type === 'video') {
          block = `
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
        const last = container.lastElementChild;
        const favIcon = last.querySelector('.fav_icon');

        if (favIcon) {
          favIcon.addEventListener('click', (e) => {
            e.stopPropagation();

            const isFavouritedNow = favIcon.classList.contains('favourited');
            const url = isFavouritedNow
              ? `/api/favourites/remove/${item.id}/`
              : `/api/favourites/add/${item.id}/`;

            fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
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

      // ⬇️ Прокрутка через наблюдатель DOM (надёжно!)
// Гарантированная прокрутка даже при долгой генерации DOM
const session = localStorage.getItem('last_session');
if (session) {
  try {
    const parsed = JSON.parse(session);
    const targetId = parsed.itemId;

    // Ждём появления нужной карточки и скроллим к ней
    let attempts = 0;
    const maxAttempts = 20;

    const scrollToCard = () => {
      const targetIcon = document.querySelector(`.fav_icon[data-id="${targetId}"]`);
      if (targetIcon) {
        const card = targetIcon.closest('.video, .audio, .file');
        if (card) {
          card.setAttribute('id', 'last_seen_card');

          const offset = card.offsetTop;
          window.scrollTo({ top: offset - 80, behavior: 'smooth' });

          setTimeout(() => {
            card.removeAttribute('id');
            localStorage.removeItem('last_session');
            console.log("✅ Прокручено к карточке ID:", targetId);
          }, 500);

          return;
        }
      }

      if (attempts++ < maxAttempts) {
        setTimeout(scrollToCard, 200);
      } else {
        console.warn("❌ Не удалось найти карточку для прокрутки");
      }
    };

    setTimeout(scrollToCard, 200);
  } catch (e) {
    console.warn("⚠️ Ошибка при прокрутке к сохранённому элементу:", e);
    localStorage.removeItem('last_session');
  }
}



    })
    .catch(err => {
      console.error("Ошибка загрузки жанра:", err);
    });
}

function openAndCollapse(url) {
  Telegram.WebApp.close();
  setTimeout(() => {
    window.location.href = url;
  }, 300);
}


function openAndRemember(item, genre) {
  const blockId = 'last_seen_card_' + item.id;

  localStorage.setItem('last_session', JSON.stringify({
    genreId: genre.id,
    genreTitle: genre.title,
    itemTitle: item.title,
    itemId: item.id,
    blockId: blockId,
    url: item.telegram_url
  }));

  Telegram.WebApp.close();
  setTimeout(() => {
    window.location.href = item.telegram_url;
  }, 400);
}


// Прокрутка к #last_seen_card и удаление id
setTimeout(() => {
  const el = document.getElementById('last_seen_card');
  if (el) {
    const offset = el.offsetTop;
    window.scrollTo({ top: offset - 80, behavior: 'smooth' });
    el.removeAttribute('id');
    localStorage.removeItem('last_session');
  }
}, 100);
