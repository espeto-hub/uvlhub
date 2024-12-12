document.addEventListener('DOMContentLoaded', function () {
    const serviceSelect = document.querySelector('select[name="service_name"]');
    const guideContent = document.getElementById('guide-content');

    serviceSelect.addEventListener('change', function () {
        const serviceName = serviceSelect.value;
        if (serviceName !== 'Select one...') {
            const encodedServiceName = encodeURIComponent(serviceName);
            fetch(`/bots/guide/${encodedServiceName}`)
                .then(response => response.text())
                .then(data => {
                    guideContent.innerHTML = data;
                })
                .catch(error => {
                    guideContent.innerHTML = 'Error loading guide.';
                    console.error('Error fetching guide:', error);
                });
        } else {
            guideContent.innerHTML = 'Please select a service to view its guide.';
        }
    });

    // Trigger the change event to load the guide content on page load
    serviceSelect.dispatchEvent(new Event('change'));
});
