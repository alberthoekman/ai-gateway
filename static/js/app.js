/**
 * AI Gateway Frontend - jQuery Implementation
 * Handles user interactions and API communication
 */

$(document).ready(function() {
    // Configuration
    const API_BASE_URL = window.location.origin;

    // DOM Elements
    const $userInput = $('#userInput');
    const $charCount = $('#charCount');
    const $analyzeBtn = $('#analyzeBtn');
    const $clearBtn = $('#clearBtn');
    const $loadingIndicator = $('#loadingIndicator');
    const $resultSection = $('#resultSection');
    const $resultContent = $('#resultContent');
    const $safetySection = $('#safetySection');
    const $safetyContent = $('#safetyContent');
    const $errorSection = $('#errorSection');
    const $errorMessage = $('#errorMessage');
    const $systemStatus = $('#systemStatus');

    // Initialize
    updateCharCount();
    checkSystemHealth();

    // Event Listeners
    $userInput.on('input', updateCharCount);
    $analyzeBtn.on('click', analyzeText);
    $clearBtn.on('click', clearForm);

    // Allow Enter+Shift to submit
    $userInput.on('keydown', function(e) {
        if (e.key === 'Enter' && e.shiftKey) {
            e.preventDefault();
            analyzeText();
        }
    });

    /**
     * Update character count display
     */
    function updateCharCount() {
        const length = $userInput.val().length;
        $charCount.text(`${length} / 10,000 karakters`);

        if (length > 9500) {
            $charCount.css('color', 'var(--error-red)');
        } else if (length > 8000) {
            $charCount.css('color', 'var(--warning-orange)');
        } else {
            $charCount.css('color', 'var(--text-gray)');
        }
    }

    /**
     * Analyze text via API
     */
    function analyzeText() {
        const text = $userInput.val().trim();

        // Validation
        if (!text) {
            showError('Voer alstublieft tekst in voor analyse.');
            return;
        }

        if (text.length > 10000) {
            showError('Tekst mag maximaal 10.000 karakters bevatten.');
            return;
        }

        // Hide previous results
        hideAllSections();

        // Show loading
        $loadingIndicator.show();
        $analyzeBtn.prop('disabled', true);

        // Make API request
        $.ajax({
            url: `${API_BASE_URL}/analyze`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ text: text }),
            timeout: 30000
        })
        .done(function(response) {
            handleSuccess(response);
        })
        .fail(function(xhr) {
            handleError(xhr);
        })
        .always(function() {
            $loadingIndicator.hide();
            $analyzeBtn.prop('disabled', false);
        });
    }

    /**
     * Handle successful API response
     */
    function handleSuccess(response) {
        if (response.status === 'success') {
            // Show AI result
            $resultContent.html(formatResult(response.result));
            $resultSection.show();

            // Show safety report
            if (response.safety_report) {
                $safetyContent.html(formatSafetyReport(response.safety_report));
                $safetySection.show();
            }

            // Scroll to results
            $resultSection[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } else if (response.status === 'blocked') {
            // PII detected - show as warning
            showBlockedMessage(response);
        } else {
            showError('Onverwachte response van server.');
        }
    }

    /**
     * Handle API error
     */
    function handleError(xhr) {
        let errorMsg = 'Er is een fout opgetreden bij het verwerken van uw verzoek.';

        if (xhr.status === 403) {
            // PII blocked
            const response = xhr.responseJSON;
            showBlockedMessage(response);
            return;
        } else if (xhr.status === 400) {
            errorMsg = 'Ongeldige invoer. Controleer uw tekst en probeer opnieuw.';
        } else if (xhr.status === 500) {
            errorMsg = 'Server fout. Probeer het later opnieuw.';
        } else if (xhr.status === 0) {
            errorMsg = 'Geen verbinding met server. Controleer uw internetverbinding.';
        } else if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMsg = xhr.responseJSON.error;
        }

        showError(errorMsg);
    }

    /**
     * Show blocked message with safety details
     */
    function showBlockedMessage(response) {
        const html = `
            <div style="margin-bottom: 15px;">
                <strong style="color: var(--error-red); font-size: 18px;">
                    🚫 Verzoek Geblokkeerd
                </strong>
            </div>
            <p style="margin-bottom: 15px;">
                ${response.message || 'Persoonlijke gegevens gedetecteerd in uw invoer.'}
            </p>
        `;

        $resultContent.html(html);
        $resultSection.show();

        if (response.safety_report) {
            $safetyContent.html(formatSafetyReport(response.safety_report, true));
            $safetySection.show();
        }

        $resultSection[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Format AI result with markdown-like rendering
     */
    function formatResult(text) {
        // Simple markdown-like formatting
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');

        return formatted;
    }

    /**
     * Format safety report as HTML
     */
    function formatSafetyReport(report, isBlocked = false) {
        const statusClass = report.pii_detected ? 'danger' : 'success';
        const statusText = report.pii_detected ? '[X] Gevonden' : '[OK] Geen gevonden';

        let html = `
            <div class="safety-item">
                <span class="safety-label">PII Scan Uitgevoerd:</span>
                <span class="safety-value success">[OK] Ja</span>
            </div>
            <div class="safety-item">
                <span class="safety-label">Persoonsgegevens:</span>
                <span class="safety-value ${statusClass}">${statusText}</span>
            </div>
            <div class="safety-item">
                <span class="safety-label">Aantal Overtredingen:</span>
                <span class="safety-value ${statusClass}">${report.violations_count}</span>
            </div>
            <div class="safety-item">
                <span class="safety-label">Strikte Modus:</span>
                <span class="safety-value">${report.strict_mode ? 'Actief' : 'Inactief'}</span>
            </div>
            <div class="safety-item">
                <span class="safety-label">Compliance:</span>
                <span class="safety-value">${report.compliance_notes}</span>
            </div>
        `;

        // Show violations if any
        if (report.violations && report.violations.length > 0) {
            html += '<div class="violations-list">';
            html += '<strong style="color: var(--error-red);">Gedetecteerde Gegevens:</strong>';

            report.violations.forEach(function(violation) {
                html += `
                    <div class="violation-item">
                        <strong>${violation.type}</strong><br>
                        Gemaskeerde waarde: <code>${violation.masked_value}</code><br>
                        Positie: ${violation.position}
                    </div>
                `;
            });

            html += '</div>';

            if (isBlocked) {
                html += `
                    <div style="margin-top: 15px; padding: 10px; background-color: var(--secondary-blue); border-radius: 4px;">
                        <strong>Wat nu?</strong><br>
                        Verwijder de persoonlijke gegevens uit uw tekst en probeer opnieuw.
                    </div>
                `;
            }
        }

        return html;
    }

    /**
     * Show error message
     */
    function showError(message) {
        hideAllSections();
        $errorMessage.html(`<strong>Fout:</strong> ${message}`);
        $errorSection.show();
    }

    /**
     * Hide all result sections
     */
    function hideAllSections() {
        $resultSection.hide();
        $safetySection.hide();
        $errorSection.hide();
    }

    /**
     * Clear form and results
     */
    function clearForm() {
        $userInput.val('');
        updateCharCount();
        hideAllSections();
        $userInput.focus();
    }

    /**
     * Check system health
     */
    function checkSystemHealth() {
        $.ajax({
            url: `${API_BASE_URL}/health`,
            method: 'GET',
            timeout: 5000
        })
        .done(function(response) {
            if (response.status === 'healthy') {
                updateSystemStatus('healthy', 'Systeem Operationeel');

                // Update stats if available
                if (response.audit_stats) {
                    console.log('Audit Stats:', response.audit_stats);
                }
            } else {
                updateSystemStatus('unhealthy', 'Systeem Problemen');
            }
        })
        .fail(function() {
            updateSystemStatus('unhealthy', 'Offline');
        });
    }

    /**
     * Update system status indicator
     */
    function updateSystemStatus(status, text) {
        const $indicator = $systemStatus.find('.status-indicator');
        const $statusText = $systemStatus.find('span:last-child');

        $indicator.removeClass('healthy unhealthy').addClass(status);
        $statusText.text(text);
    }

    // Check health every 30 seconds
    setInterval(checkSystemHealth, 30000);
});
