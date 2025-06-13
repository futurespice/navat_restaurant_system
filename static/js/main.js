// static/js/main.js

// Главный JavaScript файл проекта
document.addEventListener('DOMContentLoaded', function() {

    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Анимация при загрузке карточек
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(function() {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это?')) {
                e.preventDefault();
            }
        });
    });

    // Активация тултипов Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Обновление счетчиков в реальном времени (можно расширить)
    function updateCounters() {
        // Здесь можно добавить AJAX запросы для обновления статистики
        console.log('Обновление счетчиков...');
    }

    // Обновлять каждые 30 секунд
    setInterval(updateCounters, 30000);

    // Плавная прокрутка к якорям
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Форматирование чисел с разделителями
    const numberElements = document.querySelectorAll('[data-format-number]');
    numberElements.forEach(function(element) {
        const number = parseFloat(element.textContent);
        if (!isNaN(number)) {
            element.textContent = number.toLocaleString('ru-RU');
        }
    });
});

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', alertHTML);

    // Автоматическое удаление через 4 секунды
    setTimeout(function() {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 4000);
}

// Функция для AJAX запросов (можно использовать для обновления данных)
function makeAjaxRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Ошибка AJAX запроса:', error);
        showNotification('Произошла ошибка при выполнении запроса', 'danger');
    });
}

// Функция для динамического обновления статистики дашборда
function updateDashboardStats() {
    // Можно использовать для обновления статистики без перезагрузки
    const statCards = document.querySelectorAll('[data-stat-counter]');
    statCards.forEach(function(card) {
        // Добавить анимацию обновления
        card.style.transform = 'scale(1.05)';
        setTimeout(function() {
            card.style.transform = 'scale(1)';
        }, 200);
    });
}