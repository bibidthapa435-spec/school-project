/**
 * Popup Admin Scheduler - Simple preset selector for reliable scheduling
 * Provides a minimal, easy preset selector: Always / Today / This Week / This Month / Custom
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) return;

    const startInput = form.querySelector('input[name*="start_date"]');
    const endInput = form.querySelector('input[name*="end_date"]');

    // Build preset select and insert into schedule fieldset if present
    const scheduleFieldset = document.querySelector('fieldset:has(input[name*="start_date"])');
    if (!scheduleFieldset) return;

    const presetRow = document.createElement('div');
    presetRow.className = 'form-row';
    presetRow.style.display = 'flex';
    presetRow.style.gap = '1rem';

    const label = document.createElement('label');
    label.textContent = 'Schedule Preset';
    label.className = 'vCheckboxLabel';
    label.style.fontWeight = '600';
    label.style.marginBottom = '0.25rem';

    const select = document.createElement('select');
    select.className = 'form-control';
    select.style.maxWidth = '380px';
    select.innerHTML = `
        <option value="">Select schedule</option>
        <option value="always">Always (no dates)</option>
        <option value="today">Today Only</option>
        <option value="week">This Week</option>
        <option value="month">This Month</option>
        <option value="custom">Custom Range</option>
    `;

    const container = document.createElement('div');
    container.appendChild(label);
    container.appendChild(select);
    presetRow.appendChild(container);

    // Insert at top of schedule fieldset
    const firstRow = scheduleFieldset.querySelector('.form-row');
    if (firstRow) scheduleFieldset.insertBefore(presetRow, firstRow);
    else scheduleFieldset.appendChild(presetRow);

    function toLocalDateTimeString(d) {
        const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
        return local.toISOString().slice(0, 16);
    }

    select.addEventListener('change', function() {
        const val = this.value;
        const now = new Date();
        if (!startInput || !endInput) return;

        switch (val) {
            case 'always':
                startInput.value = '';
                endInput.value = '';
                break;
            case 'today':
                startInput.value = toLocalDateTimeString(now);
                const endTonight = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59);
                endInput.value = toLocalDateTimeString(endTonight);
                break;
            case 'week':
                startInput.value = toLocalDateTimeString(now);
                const weekEnd = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
                endInput.value = toLocalDateTimeString(weekEnd);
                break;
            case 'month':
                startInput.value = toLocalDateTimeString(now);
                const monthEnd = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
                endInput.value = toLocalDateTimeString(monthEnd);
                break;
            case 'custom':
                // leave values for manual input
                break;
            default:
                break;
        }

        // Dispatch change events so Django admin validation can react
        startInput.dispatchEvent(new Event('change'));
        endInput.dispatchEvent(new Event('change'));
    });

    // If the admin provided a schedule_preset field (model form), wire it to keep sync
    const presetField = form.querySelector('select[name="schedule_preset"]');
    if (presetField) {
        // Keep the invisible field in sync for potential server-side use
        select.addEventListener('change', function() {
            presetField.value = this.value;
        });
    }
});
