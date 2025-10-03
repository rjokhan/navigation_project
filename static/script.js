// ---- GENRES ----
(async function loadGenres() {
  const container = document.querySelector('.container_genre');
  if (!container) return;
  container.innerHTML = '<div class="loading">Рубрикалар рўйхати юкланяпти...</div>';

  try {
    // 1) БЕРЁМ СПИСОК ЖАНРОВ (относительный URL, чтобы не упереться в 127.0.0.1 и CORS)
    const res = await fetch('/api/genres/', { credentials: 'same-origin' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!Array.isArray(data)) {
      container.innerHTML = "<div class='error'>Нотоғри формат</div>";
      return;
    }

    container.innerHTML = '';

    // helper для безопасного числа
    const num = (v) => (Number.isFinite(v) ? v : 0);

    // 2) РЕНДЕРИМ КАЖДЫЙ ЖАНР
    for (const genre of data) {
      const genreDiv = document.createElement('div');
      genreDiv.className = 'genre';

      const count = document.createElement('div');
      count.className = 'count';
      count.textContent = '…'; // скелет до реального подсчёта

      const name = document.createElement('div');
      name.className = 'genre_name';

      // Чистим заголовок: удаляем лидирующее "A " если оно уже пришло
      let cleanTitle = genre.title || '';
      if (cleanTitle.startsWith('A ')) cleanTitle = cleanTitle.slice(2);
      name.innerHTML = `<span class="red">A </span>${cleanTitle}`;

      genreDiv.appendChild(count);
      genreDiv.appendChild(name);

      // ---- Подсчёт количества контента ----
      // Пытаемся использовать то, что уже пришло, иначе — отдельный запрос /api/content/<id>/
      (async () => {
        // 1) если API уже вернул items/count/total
        const directCount =
          num(genre.total) ||
          num(genre.count) ||
          (Array.isArray(genre.items) ? genre.items.length : 0);

        if (directCount) {
          count.textContent = directCount > 99 ? '99+' : String(directCount);
          return;
        }

        // 2) иначе добираем по /api/content/<genre_id>/
        try {
          const r = await fetch(`/api/content/${genre.id}/?page=1`, { credentials: 'same-origin' });
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          const j = await r.json();
          const total =
            num(j?.total) ||
            num(j?.count) ||
            (Array.isArray(j?.items) ? j.items.length : 0);

          count.textContent = total > 99 ? '99+' : String(total);
        } catch {
          // если и это не удалось — показываем 0
          count.textContent = '0';
        }
      })();

      // ---- Переход в контент: ИСПОЛЬЗУЕМ DJANGO-ПУТЬ ----
      genreDiv.onclick = () => {
        const genreId = genre.id;
        const titleParam = encodeURIComponent(genre.title || '');
        // Было: content.html?...
        // Нужно: /content/?genre_id=...&genre_title=...
        window.location.href = `/content/?genre_id=${genreId}&genre_title=${titleParam}`;
      };

      container.appendChild(genreDiv);
    }
  } catch (error) {
    console.error('Ошибка при загрузке жанров:', error);
    container.innerHTML = "<div class='error'>Рубрикаларни йўклашда хатолик бўлди</div>";
  }
})();

// ---- SEARCH ----
(function wireSearch() {
  const form = document.querySelector('.searcher');
  const input = document.querySelector('.searcher_block');
  if (!form || !input) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const query = input.value.trim();
    if (!query) return;

    // Было: searched.html?query=...
    // Нужно: /searched/?query=... (под Django)
    window.location.href = `/searched/?query=${encodeURIComponent(query)}`;
  });
})();
