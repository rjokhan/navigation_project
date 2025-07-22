const telegramId = localStorage.getItem('telegram_id');

if (!telegramId) {
  document.getElementById('user_info').innerHTML = '<p>Ошибка: Telegram ID не найден.</p>';
} else {
  fetch('https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Token': 'b0e63095ee9d51fd0188f1877d63c0b850bc4965a61527c9'
    },
    body: JSON.stringify({ telegram_id: telegramId })
  })
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('user_info');
    if (!data.success) {
      container.innerHTML = `<p>${data.message}</p>`;
      return;
    }

    const user = data.user || {}; // ← когда в будущем добавят данные

    container.innerHTML = `
      <p><strong>ФИО:</strong> ${user.full_name || '—'}</p>
      <p><strong>Город:</strong> ${user.city || '—'}</p>
      <p><strong>Резидент:</strong> ${user.is_resident ? '✅ Да' : '❌ Нет'}</p>
      <p><strong>Срок резидентства:</strong> ${user.residency_until || '—'}</p>
    `;
  })
  .catch(error => {
    document.getElementById('user_info').innerHTML = '<p>Ошибка при получении данных</p>';
    console.error(error);
  });
}
