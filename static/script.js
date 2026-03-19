// Fetch years from the API and populate the dropdown
async function loadYears() {
    const select = document.getElementById('year-select');
    const selection = document.getElementById('selection');

    try {
        const response = await fetch('/years');
        if (!response.ok) {
            throw new Error('Failed to fetch years');
        }

        const data = await response.json();
        select.innerHTML = '<option value="">Pick a year...</option>';

        data.years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            select.appendChild(option);
        });

        select.disabled = false;
        selection.textContent = 'Choose a year to see more.';
    } catch (error) {
        console.error('Error loading years:', error);
        select.innerHTML = '<option value="">Error loading years</option>';
        select.disabled = true;
        selection.textContent = 'Unable to load years right now. Please try again later.';
    }
}

async function loadTeams(year) {
    const teamList = document.getElementById('team-list');

    teamList.textContent = 'Loading teams…';
    try {
        const response = await fetch(`/teams?year=${encodeURIComponent(year)}`);
        if (!response.ok) {
            throw new Error('Failed to load teams');
        }

        const data = await response.json();
        const teams = (data.teams || []).map(team => team.name).filter(Boolean);

        if (!teams.length) {
            teamList.textContent = 'No teams found for that year.';
            return;
        }

        const list = document.createElement('ul');
        list.className = 'team-list-items';
        teams.sort().forEach(name => {
            const item = document.createElement('li');
            item.textContent = name;
            list.appendChild(item);
        });

        teamList.innerHTML = '';
        teamList.appendChild(list);
    } catch (error) {
        console.error('Error loading teams:', error);
        teamList.textContent = 'Could not load teams right now.';
    }
}

function handleYearSelection(event) {
    const year = event.target.value;
    const selection = document.getElementById('selection');

    if (!year) {
        selection.textContent = 'Choose a year to see more.';
        document.getElementById('team-list').textContent = 'Pick a year to load teams.';
        return;
    }

    selection.textContent = `✨ You picked ${year}! ✨`;
    loadTeams(year);
}

// Load years when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadYears();

    const select = document.getElementById('year-select');
    select.addEventListener('change', handleYearSelection);
});