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

    const user = data.user_info || {};
    const tariff = Array.isArray(data.tariffs) && data.tariffs.length > 0 ? data.tariffs[0] : null;

    container.innerHTML = `
      <p><strong>Имя:</strong> ${user.first_name || user.full_name || user.username || '—'}</p>
      <p><strong>Телефон:</strong> ${user.phone_number || '—'}</p>
      <p><strong>Тариф:</strong> ${tariff ? tariff.name : '—'}</p>
      <p><strong>Подписка до:</strong> ${tariff ? tariff.expires_at.split(' ')[0] : '—'}</p>
    `;
  })
  .catch(error => {
    document.getElementById('user_info').innerHTML = '<p>Ошибка при получении данных</p>';
    console.error(error);
  });
}
