fetch('http://127.0.0.1:8000/api/genres/')
  .then(response => response.json())
  .then(data => {
    const container = document.querySelector('.container_genre');
    container.innerHTML = '';

    data.forEach(genre => {
      const genreDiv = document.createElement('div');
      genreDiv.className = 'genre';

      const count = document.createElement('div');
      count.className = 'count';
      count.textContent = genre.items.length;

      const name = document.createElement('div');
      name.className = 'genre_name';
      name.innerHTML = `<span class="red">A </span>${genre.title.split(' ')[1]}`;

      genreDiv.appendChild(count);
      genreDiv.appendChild(name);

      genreDiv.onclick = () => {
        if (genre.items.length > 0) {
          const genreId = genre.id;
          window.location.href = `content.html?genre_id=${genreId}&genre_title=${encodeURIComponent(genre.title)}`;
        } else {
          alert('Контент пока не добавлен');
        }
      };

      container.appendChild(genreDiv);
    });
  })
  .catch(error => {
    console.error('Ошибка при загрузке жанров:', error);
  });

document.querySelector('.searcher').addEventListener('submit', function (e) {
  e.preventDefault();
  const query = document.querySelector('.searcher_block').value.trim();
  if (query) {
    window.location.href = `searched.html?query=${encodeURIComponent(query)}`;
  }
});
