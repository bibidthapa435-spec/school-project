/** Keep the popup notice preset field and quick schedule buttons in sync. */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) return;

    const startInput = form.querySelector('input[name="start_date"]');
    const endInput = form.querySelector('input[name="end_date"]');
    const presetField = form.querySelector('select[name="schedule_preset"]');
    if (!startInput || !endInput || !presetField) return;

    function formatLocalDateTime(date) {
        const pad = value => String(value).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
            `T${pad(date.getHours())}:${pad(date.getMinutes())}`;
    }

    function applyPreset(value) {
        const now = new Date();
        let start = '';
        let end = '';

        switch (value) {
            case 'today': {
                start = formatLocalDateTime(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0));
                end = formatLocalDateTime(new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59));
                break;
            }
            case 'week': {
                const daysSinceMonday = (now.getDay() + 6) % 7;
                const monday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - daysSinceMonday, 0, 0);
                const sundayEnd = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + 6, 23, 59);
                start = formatLocalDateTime(monday);
                end = formatLocalDateTime(sundayEnd);
                break;
            }
            case 'month': {
                const monthStart = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0);
                const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59);
                start = formatLocalDateTime(monthStart);
                end = formatLocalDateTime(monthEnd);
                break;
            }
            case 'always':
                break;
            case 'custom':
                // Keep the manually entered range.
                return;
            default:
                return;
        }

        startInput.value = start;
        endInput.value = end;
        startInput.dispatchEvent(new Event('change', { bubbles: true }));
        endInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    presetField.addEventListener('change', function() {
        applyPreset(this.value);
    });
});
