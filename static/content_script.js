const params = new URLSearchParams(window.location.search);
const genreId = params.get("genre_id");
const genreTitle = params.get("genre_title");

document.querySelector(".choosed_genre").innerHTML = `<span class="red">A </span>${genreTitle?.split(" ")[1] || ''}:`;

const telegramId = localStorage.getItem('telegram_id'); // заранее получен

if (!telegramId) {
  alert("Ошибка: Telegram ID не найден");
}

let userFavourites = [];

fetch(`http://127.0.0.1:8000/api/favourites/?telegram_id=${telegramId}`)
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
  fetch(`http://127.0.0.1:8000/api/genres/`)
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
        const favIconHTML = `<div class="fav_icon ${favClass}" data-id="${item.id}"></div>`;

        let block = '';
        const openLink = `window.open('${item.telegram_url}', '_blank')`;

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
                <div class="static_icon"><img src="/images/audio_icon.png"></div>
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
                <div class="static_icon"><img src="/images/file_icon.png"></div>
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

        favIcon.addEventListener('click', (e) => {
          e.stopPropagation();

          const isFavouritedNow = favIcon.classList.contains('favourited');
          const url = isFavouritedNow
            ? `http://127.0.0.1:8000/api/favourites/remove/${item.id}/`
            : `http://127.0.0.1:8000/api/favourites/add/${item.id}/`;

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
            }
          })
          .catch(err => console.error("Ошибка при обновлении избранного:", err));
        });

        allCards.push({ ...item, genreId: genre.id });
      });

      localStorage.setItem('allCards', JSON.stringify(allCards));
    })
    .catch(err => {
      console.error("Ошибка загрузки жанра:", err);
    });
}
