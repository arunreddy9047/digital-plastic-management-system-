// static/js/main.js
// Handles AJAX Submissions for Forms throughout the E-Plastic Management App

document.addEventListener('DOMContentLoaded', function() {
    const entryForm = document.getElementById('entryForm');
    if (entryForm) {
        entryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const teamSelect = document.getElementById('team_id');
            const quantityInput = document.getElementById('quantity_kg');
            if (!quantityInput) {
                alert(translate('add_record_error'));
                return;
            }

            const data = {
                location_id: document.getElementById('location_id').value,
                plastic_type_id: document.getElementById('plastic_type_id').value,
                quantity_kg: parseFloat(quantityInput.value),
                date: document.getElementById('date').value,
                recorded_by: document.getElementById('recorded_by').value.trim(),
                team_id: teamSelect ? teamSelect.value : null
            };

            fetch('/api/add-record', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => {
                if (!res.ok) throw new Error(translate('network_error'));
                return res.json();
            })
            .then(result => {
                alert(result.message);
                entryForm.reset();
            })
            .catch(err => {
                console.error(err);
                alert(translate('add_record_error'));
            });
        });
    }
});

function addTeam() {
    const team_name = document.getElementById('team_name').value.trim();
    const team_leader = document.getElementById('team_leader').value.trim();
    const location_id = document.getElementById('team_location').value;

    if (!team_name) {
        alert(translate('team_name_required'));
        return;
    }

    const data = {
        team_name: team_name,
        team_leader: team_leader || '',
        location_id: location_id || null
    };

    fetch('/api/add-team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {
        alert(result.message);
        location.reload();
    })
    .catch(err => {
        console.error(err);
        alert(translate('team_add_error'));
    });
}

function addVolunteer() {
    const name = document.getElementById('vol_name').value.trim();
    const email = document.getElementById('vol_email').value.trim();
    const phone = document.getElementById('vol_phone').value.trim();
    const team_id = document.getElementById('vol_team').value;
    const joined_date = document.getElementById('vol_date').value;
    const contribution_type = document.getElementById('vol_contribution').value.trim();
    const hours_worked = document.getElementById('vol_hours').value;
    const impact = document.getElementById('vol_impact').value.trim();

    if (!name || !email || !joined_date) {
        alert(translate('volunteer_required_fields'));
        return;
    }

    const data = {
        name: name,
        email: email,
        phone: phone || '',
        team_id: team_id || null,
        joined_date: joined_date,
        contribution_type: contribution_type || '',
        hours_worked: parseInt(hours_worked) || 0,
        impact: impact || ''
    };

    fetch('/api/add-volunteer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (!res.ok) throw new Error('Server returned an error');
        return res.json();
    })
    .then(result => {
        alert(result.message);
        location.reload();
    })
    .catch(err => {
        console.error(err);
        alert(translate('volunteer_add_error'));
    });
}
