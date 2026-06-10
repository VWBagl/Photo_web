// =====================================================================
// 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ И СОСТОЯНИЕ
// =====================================================================
window.CURRENT_USER = {
    id: document.body.dataset.userId ? parseInt(document.body.dataset.userId, 10) : null,
    is_moderator: document.body.dataset.isModerator === 'true'
};

window.commentFormState = {
    mode: 'new', // 'new' | 'reply' | 'edit'
    parentId: null,
    editCommentId: null,
    editOriginalText: ''
};

// =====================================================================
// 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// =====================================================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateHeaderCounter(count) {
    const header = document.querySelector('.card-header h5');
    if (header) header.textContent = `Комментарии (${count})`;
}

function buildCommentHTML(data) {
    const isReply = data.parent_id !== null;
    const bgClass = isReply ? 'bg-white mb-2 p-2' : 'bg-light mb-3 p-2';
    const textClass = isReply ? 'small' : '';
    const authorClass = isReply ? 'text-primary' : '';
    const dateStr = data.created_at || data.updated_at || '';
    const safeText = data.text.replace(/"/g, '&quot;').replace(/\n/g, '<br>');
    const canModify = data.is_author || window.CURRENT_USER.is_moderator;

    let buttonsHtml = '';
    if (!isReply) {
        if (canModify) buttonsHtml += `<button type="button" class="comment-action-link comment-edit-btn">Изменить</button>`;
        buttonsHtml += `<button type="button" class="comment-action-link comment-reply-btn" data-parent-id="${data.id}">Ответить</button>`;
        if (canModify) buttonsHtml += `<button type="button" class="comment-action-link comment-delete-btn">Удалить</button>`;
    } else {
        if (canModify) buttonsHtml += `<button type="button" class="comment-action-link comment-edit-btn">Изменить</button>`;
        if (canModify) buttonsHtml += `<button type="button" class="comment-action-link comment-delete-btn">Удалить</button>`;
    }

    return `<div class="${bgClass} rounded comment-item" data-comment-id="${data.id}" data-text="${safeText}" data-has-replies="false">
        <div class="d-flex justify-content-between small text-muted mb-1">
            <strong class="${authorClass}">${data.author}</strong>
            <span>${dateStr}</span>
        </div>
        <p class="mb-1 ${textClass} comment-text">${safeText}</p>
        <div class="d-flex gap-3 mt-1">${buttonsHtml}</div>
    </div>`;
}

// =====================================================================
// 3. API ЗАПРОСЫ (КОММЕНТАРИИ)
// =====================================================================
function submitComment(text, photoId, parentId, onSuccess) {
    if (!text?.trim()) return;
    fetch('/api/comments/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_id: photoId, text, parent_id: parentId })
    })
        .then(res => res.ok ? res.json() : res.json().then(d => { throw new Error(d.error) }))
        .then(data => {
            onSuccess(buildCommentHTML(data));
            updateHeaderCounter(data.photo_comments_count);
        })
        .catch(err => alert(err.message));
}

function updateComment(commentId, text, onSuccess) {
    // Используем PATCH и передаём ID в URL, а не в теле запроса
    fetch(`/api/comments/${commentId}/`, {
        method: 'PATCH',
        headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
        .then(res => res.ok ? res.json() : res.json().then(d => { throw new Error(d.error) }))
        .then(data => onSuccess(data))
        .catch(err => alert(err.message));
}

function deleteComment(commentId, onSuccess) {
    // Используем DELETE и передаём ID в URL
    fetch(`/api/comments/${commentId}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
    })
        .then(res => res.ok ? res.json() : res.json().then(d => { throw new Error(d.error) }))
        .then(data => onSuccess(data.photo_comments_count))
        .catch(err => alert(err.message));
}

// =====================================================================
// 4. УПРАВЛЕНИЕ ИНТЕРФЕЙСОМ (UI)
// =====================================================================
function setFormMode(mode, options = {}) {
    window.commentFormState.mode = mode;
    const contextEl = document.getElementById('comment-context');
    const iconEl = document.getElementById('context-icon');
    const titleEl = document.getElementById('context-title');
    const textEl = document.getElementById('context-text');
    const textarea = document.getElementById('comment-textarea');

    if (mode === 'new') {
        contextEl?.classList.add('d-none');
        if (textarea) textarea.placeholder = 'Напишите комментарий...';
        if (textarea) textarea.value = '';
        window.commentFormState.parentId = null;
        window.commentFormState.editCommentId = null;
        window.commentFormState.editOriginalText = '';
    } else if (mode === 'reply') {
        contextEl?.classList.remove('d-none');
        iconEl.textContent = '💬';
        titleEl.textContent = `Ответ пользователю ${options.author || ''}`;
        textEl.textContent = '';
        if (textarea) textarea.placeholder = 'Ваш ответ...';
        window.commentFormState.parentId = options.parentId;
        if (textarea) textarea.focus();
    } else if (mode === 'edit') {
        contextEl?.classList.remove('d-none');
        iconEl.textContent = '✏️';
        titleEl.textContent = 'Редактирование';
        textEl.textContent = `: ${options.originalText || ''}`;
        if (textarea) textarea.placeholder = 'Отредактированный комментарий...';
        if (textarea) textarea.value = options.originalText || '';
        window.commentFormState.editCommentId = options.commentId;
        window.commentFormState.editOriginalText = options.originalText || '';
        if (textarea) textarea.focus();
    }
}

// =====================================================================
// 5. ОБРАБОТЧИКИ СОБЫТИЙ (КЛИКИ И ФОРМЫ)
// =====================================================================
document.addEventListener('click', function (e) {
    // Ответить
    const replyBtn = e.target.closest('.comment-reply-btn');
    if (replyBtn) {
        const item = replyBtn.closest('.comment-item');
        setFormMode('reply', { parentId: item?.dataset.commentId, author: item?.querySelector('strong')?.textContent || '' });
        return;
    }
    // Удалить
    const deleteBtn = e.target.closest('.comment-delete-btn');
    if (deleteBtn) {
        const item = deleteBtn.closest('.comment-item');
        const commentId = item?.dataset.commentId;
        if (!commentId) return;
        if (item?.dataset.hasReplies === 'true') { alert('Нельзя удалить комментарий, на который уже есть ответы'); return; }
        if (!confirm('Вы уверены, что хотите удалить комментарий?')) return;

        deleteComment(commentId, function (photoCount) {
            item?.remove();
            const parent = item?.parentElement;
            if (parent?.classList.contains('border-start') && parent.children.length === 0) parent.remove();
            updateHeaderCounter(photoCount);
        });
        return;
    }
    // Изменить
    const editBtn = e.target.closest('.comment-edit-btn');
    if (editBtn) {
        const item = editBtn.closest('.comment-item');
        setFormMode('edit', {
            commentId: item?.dataset.commentId,
            originalText: item?.dataset.text || item.querySelector('.comment-text')?.textContent || ''
        });
        return;
    }
    // Отмена контекста
    if (e.target.closest('#cancel-context')) {
        setFormMode('new');
        return;
    }
});

document.addEventListener('submit', function (e) {
    if (e.target.id === 'comment-form') {
        e.preventDefault();
        const textarea = document.getElementById('comment-textarea');
        const text = textarea?.value?.trim();
        if (!text) return;

        const photoId = document.querySelector('[data-photo-id]')?.dataset.photoId || window.location.pathname.split('/').filter(Boolean)[1];
        const state = window.commentFormState;

        if (state.mode === 'reply' && state.parentId) {
            submitComment(text, photoId, state.parentId, function (html) {
                const parentItem = document.querySelector(`[data-comment-id="${state.parentId}"]`);
                if (!parentItem) return;
                let replyContainer = parentItem.querySelector('.border-start');
                if (!replyContainer) {
                    replyContainer = document.createElement('div');
                    replyContainer.className = 'ms-4 mt-2 border-start border-secondary ps-2';
                    parentItem.appendChild(replyContainer);
                }
                replyContainer.insertAdjacentHTML('beforeend', html);
                setFormMode('new');
            });
        } else if (state.mode === 'edit' && state.editCommentId) {
            updateComment(state.editCommentId, text, function (data) {
                const item = document.querySelector(`[data-comment-id="${state.editCommentId}"]`);
                if (item) {
                    const textEl = item.querySelector('.comment-text');
                    if (textEl) textEl.innerHTML = data.text.replace(/\n/g, '<br>');
                    item.dataset.text = data.text;
                }
                setFormMode('new');
            });
        } else {
            submitComment(text, photoId, null, function (html) {
                const list = document.getElementById('comments-list');
                if (list) {
                    list.insertAdjacentHTML('afterbegin', html);
                    list.querySelector('.text-muted.text-center.py-3')?.remove();
                }
                setFormMode('new');
            });
        }
    }
});

document.addEventListener('keydown', function (e) {
    if (e.target.id !== 'comment-textarea') return;
    const textarea = e.target;
    const state = window.commentFormState;

    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const form = document.getElementById('comment-form');
        if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        return;
    }
    if (e.key === 'Escape') {
        if (state.mode !== 'new') {
            setFormMode('new');
            return;
        }
        if (textarea.value.trim() !== '') {
            textarea.value = '';
            textarea.blur();
        } else {
            textarea.blur();
        }
    }
});

// =====================================================================
// 6. ГОЛОСОВАНИЕ (VOTE)
// =====================================================================
document.addEventListener('DOMContentLoaded', function () {
    // Показ Toast при клике на голосование для неавторизованных
    document.querySelectorAll('.vote-trigger[aria-disabled="true"]').forEach(function (trigger) {
        trigger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const toastEl = document.getElementById('authRequiredToast');
            const toast = new bootstrap.Toast(toastEl, { delay: 10000 });
            toast.show();
        });
    });

    // Основная логика голосования
    document.addEventListener('click', function (e) {
        const trigger = e.target.closest('.vote-trigger');
        if (!trigger || trigger.getAttribute('aria-disabled') === 'true' || !trigger.dataset.photoId) {
            return;
        }
        e.preventDefault();
        e.stopPropagation();

        const photoId = parseInt(trigger.dataset.photoId, 10);
        const countEl = trigger.querySelector('.vote-count');

        fetch('/api/vote/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ photo_id: photoId })
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => { throw new Error(data.error || 'Ошибка голосования'); });
                }
                return response.json();
            })
            .then(data => {
                if (countEl) countEl.textContent = data.votes_count;
            })
            .catch(error => {
                console.error('Vote error:', error);
                alert(error.message);
            });
    });
});