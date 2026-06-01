document.addEventListener('keydown', function (e) {
    if (e.target.id === 'agent-query-input' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();

        var btn = document.getElementById('agent-submit-btn');
        if (!btn) return;

        // React 17+ stores the component's event handlers under a key that
        // starts with '__reactProps$' on the DOM node itself.  Calling onClick
        // directly is the most reliable way to trigger Dash's n_clicks update
        // without relying on event-delegation bubbling.
        var rKey = Object.keys(btn).find(function (k) {
            return k.startsWith('__reactProps');
        });

        if (rKey && btn[rKey] && typeof btn[rKey].onClick === 'function') {
            btn[rKey].onClick({ preventDefault: function () {}, stopPropagation: function () {} });
        } else {
            // Fallback for older React versions
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
        }
    }
});
